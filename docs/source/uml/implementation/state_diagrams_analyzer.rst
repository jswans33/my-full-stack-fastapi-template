UML State Diagram Analyzer
========================

This section details the analyzer component for state diagram extraction. The analyzer uses Python's Abstract Syntax Tree (AST) module to analyze Python code and extract state patterns and transitions.

State Analyzer Overview
---------------------

The state analyzer consists of several key components:

1. **StateAttributeVisitor**: Finds attributes related to state in Python code
2. **StateTransitionVisitor**: Extracts state transitions from a Python class
3. **StatePatternDetector**: Detects state pattern usage in a class
4. **StateAnalyzer**: Main analyzer class that coordinates the extraction process

These components work together to analyze Python code and extract state diagrams.

Implementation
------------

The following code shows the implementation of the state analyzer in ``utils/state_extractor/analyzer.py``:

State Attribute Visitor
~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    class StateAttributeVisitor(ast.NodeVisitor):
        """AST visitor that finds attributes related to state."""
        
        def __init__(self):
            self.state_attributes: List[ast.Attribute] = []
        
        def visit_Attribute(self, node: ast.Attribute) -> None:
            """Visit an attribute access node."""
            if (
                isinstance(node.value, ast.Name)
                and node.value.id == "self"
                and node.attr == "state"
            ):
                self.state_attributes.append(node)
            
            self.generic_visit(node)

State Transition Visitor
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    class StateTransitionVisitor(ast.NodeVisitor):
        """AST visitor that extracts state transitions from a Python class."""
        
        def __init__(self, class_name: str):
            self.class_name = class_name
            self.transitions: List[TransitionInfo] = []
            self.states: Dict[str, StateInfo] = {}
            self.current_method: Optional[str] = None
            self.current_line: int = 0
        
        def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
            """Visit a function definition node."""
            self.current_method = node.name
            self.current_line = node.lineno
            
            # Extract state information from method decorators
            for decorator in node.decorator_list:
                self._process_decorator(decorator)
            
            # Look for state transitions in the method body
            self._find_state_transitions(node)
            
            # Continue visiting the method body
            self.generic_visit(node)
            
            # Clear current method tracking
            self.current_method = None
        
        def _process_decorator(self, decorator: ast.expr) -> None:
            """Process a decorator to extract state information."""
            # Handle @state decorator
            if isinstance(decorator, ast.Call) and isinstance(decorator.func, ast.Name):
                if decorator.func.id == "state":
                    # @state("state_name")
                    if decorator.args:
                        state_name = self._extract_string_value(decorator.args[0])
                        if state_name:
                            # Generate a stable ID
                            state_id = f"state_{len(self.states)}"
                            
                            # Extract additional info from keywords
                            is_initial = self._extract_keyword_value(
                                decorator, "initial", False
                            )
                            is_final = self._extract_keyword_value(
                                decorator, "final", False
                            )
                            
                            # Create state info
                            state_info = StateInfo(
                                state_name=state_name,
                                state_id=state_id,
                                method_name=self.current_method,
                                is_initial=is_initial,
                                is_final=is_final,
                                line_number=self.current_line,
                            )
                            
                            self.states[state_name] = state_info
                
                # Handle @transition decorator
                elif decorator.func.id == "transition":
                    # @transition(source="state1", target="state2", event="event_name")
                    source = self._extract_keyword_value(decorator, "source", "")
                    target = self._extract_keyword_value(decorator, "target", "")
                    event = self._extract_keyword_value(decorator, "event", None)
                    guard = self._extract_keyword_value(decorator, "guard", None)
                    action = self._extract_keyword_value(decorator, "action", None)
                    
                    if source and target:
                        transition_info = TransitionInfo(
                            source_state=source,
                            target_state=target,
                            event=event,
                            guard=guard,
                            action=action,
                            method_name=self.current_method,
                            line_number=self.current_line,
                        )
                        
                        self.transitions.append(transition_info)
        
        def _extract_string_value(self, node: ast.expr) -> Optional[str]:
            """Extract a string value from an AST node."""
            if isinstance(node, ast.Str):
                return node.s
            elif isinstance(node, ast.Constant) and isinstance(node.value, str):
                return node.value
            return None
        
        def _extract_keyword_value(self, call_node: ast.Call, keyword: str, default=None):
            """Extract a keyword argument value from a function call."""
            for kw in call_node.keywords:
                if kw.arg == keyword:
                    if isinstance(kw.value, ast.Str):
                        return kw.value.s
                    elif isinstance(kw.value, ast.Constant):
                        return kw.value.value
                    elif isinstance(kw.value, ast.Name):
                        # For variables like True, False
                        if kw.value.id == "True":
                            return True
                        elif kw.value.id == "False":
                            return False
                    # For complex expressions, return string representation
                    return ast.unparse(kw.value).strip()
            return default
        
        def _find_state_transitions(self, node: ast.FunctionDef) -> None:
            """Find state transitions in a method body."""
            # First find all assignments to self.state
            state_attrs = []
            attr_visitor = StateAttributeVisitor()
            attr_visitor.visit(node)
            state_attrs.extend(attr_visitor.state_attributes)
            
            # Process each state attribute assignment
            for stmt in ast.walk(node):
                if (
                    isinstance(stmt, ast.Assign)
                    and isinstance(stmt.targets[0], ast.Attribute)
                    and isinstance(stmt.targets[0].value, ast.Name)
                    and stmt.targets[0].value.id == "self"
                    and stmt.targets[0].attr == "state"
                ):
                    # Found an assignment like "self.state = new_state"
                    target_state = self._extract_state_from_assignment(stmt.value)
                    
                    if target_state:
                        # Look for condition checks before this assignment
                        current_state = self._extract_current_state_from_context(stmt)
                        
                        if current_state:
                            # Create a transition
                            transition_info = TransitionInfo(
                                source_state=current_state,
                                target_state=target_state,
                                method_name=self.current_method,
                                line_number=getattr(stmt, "lineno", self.current_line),
                            )
                            
                            self.transitions.append(transition_info)
        
        def _extract_state_from_assignment(self, value: ast.expr) -> Optional[str]:
            """Extract state name from an assignment value."""
            if isinstance(value, ast.Str):
                return value.s
            elif isinstance(value, ast.Constant) and isinstance(value.value, str):
                return value.value
            
            # Handle variable references
            elif isinstance(value, ast.Name):
                # This could be a variable holding a state name
                # For simplicity, we'll use the variable name as state name
                return value.id
            
            return None
        
        def _extract_current_state_from_context(self, stmt: ast.AST) -> Optional[str]:
            """
            Attempt to extract the current state from the context around a statement.
            
            Looks for conditions like "if self.state == 'old_state':" before the statement.
            """
            # This is a simplified approach that looks for certain patterns
            # A more robust solution would need control flow analysis
            
            # Look for a parent If node
            parent_if = None
            for parent in ast.iter_child_nodes(stmt):
                if isinstance(parent, ast.If):
                    parent_if = parent
                    break
            
            if parent_if and isinstance(parent_if.test, ast.Compare):
                compare = parent_if.test
                
                # Check for comparison like self.state == 'state_name'
                if (
                    isinstance(compare.left, ast.Attribute)
                    and isinstance(compare.left.value, ast.Name)
                    and compare.left.value.id == "self"
                    and compare.left.attr == "state"
                    and len(compare.ops) == 1
                    and isinstance(compare.ops[0], ast.Eq)
                    and len(compare.comparators) == 1
                ):
                    
                    # Extract state name from right side
                    comparator = compare.comparators[0]
                    if isinstance(comparator, ast.Str):
                        return comparator.s
                    elif isinstance(comparator, ast.Constant) and isinstance(
                        comparator.value, str
                    ):
                        return comparator.value
            
            return None

State Pattern Detector
~~~~~~~~~~~~~~~~~~~

.. code-block:: python

    class StatePatternDetector(ast.NodeVisitor):
        """AST visitor that detects state pattern usage in a class."""
        
        def __init__(self):
            self.has_state_field = False
            self.state_transitions: Dict[Tuple[str, str], List[ast.AST]] = {}
        
        def visit_ClassDef(self, node: ast.ClassDef) -> None:
            """Visit a class definition to look for state pattern."""
            # Look for state field in attributes
            for body_item in node.body:
                if isinstance(body_item, ast.Assign):
                    for target in body_item.targets:
                        if isinstance(target, ast.Name) and target.id == "state":
                            self.has_state_field = True
            
            # Visit all methods
            self.generic_visit(node)
        
        def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
            """Visit a method to look for state transitions."""
            # Skip if it's not an instance method
            if not node.args.args or node.args.args[0].arg != "self":
                return
            
            # Look for state changes in the method
            for body_item in ast.walk(node):
                if isinstance(body_item, ast.Assign):
                    for target in body_item.targets:
                        if (
                            isinstance(target, ast.Attribute)
                            and isinstance(target.value, ast.Name)
                            and target.value.id == "self"
                            and target.attr == "state"
                        ):
                            # Found a state change
                            # For simplicity, record the node
                            method_name = node.name
                            self.state_transitions.setdefault((method_name, ""), []).append(
                                body_item
                            )

Main State Analyzer
~~~~~~~~~~~~~~~~

.. code-block:: python

    class StateAnalyzer:
        """Analyzer for extracting state diagrams from Python code."""
        
        def __init__(self, root_dir: str | Path = "."):
            self.root_dir = Path(root_dir)
            self.class_transitions: Dict[str, List[TransitionInfo]] = {}
            self.class_states: Dict[str, Dict[str, StateInfo]] = {}
        
        def analyze_file(self, file_path: str | Path) -> None:
            """Analyze a single Python file for state patterns."""
            path = Path(file_path) if isinstance(file_path, str) else file_path
            
            # Read and parse the file
            with open(path, encoding="utf-8") as f:
                code = f.read()
            
            try:
                tree = ast.parse(code)
                
                # Look for classes with state pattern
                for node in ast.iter_child_nodes(tree):
                    if isinstance(node, ast.ClassDef):
                        class_name = node.name
                        
                        # First detect if the class uses state pattern
                        detector = StatePatternDetector()
                        detector.visit(node)
                        
                        if detector.has_state_field or detector.state_transitions:
                            # Class uses state pattern, extract transitions
                            visitor = StateTransitionVisitor(class_name)
                            visitor.visit(node)
                            
                            # Store the results
                            self.class_transitions[class_name] = visitor.transitions
                            self.class_states[class_name] = visitor.states
                
            except SyntaxError as e:
                print(f"Syntax error in {file_path}: {e}")
        
        def analyze_directory(self, dir_path: str | Path | None = None) -> None:
            """Analyze all Python files in a directory for state patterns."""
            if dir_path is None:
                target_dir = self.root_dir
            else:
                target_dir = Path(dir_path) if isinstance(dir_path, str) else dir_path
            
            # Walk through the directory and analyze Python files
            for root, _, files in os.walk(target_dir):
                for file in files:
                    if file.endswith(".py"):
                        file_path = os.path.join(root, file)
                        self.analyze_file(file_path)
        
        def generate_state_diagram(self, class_name: str) -> StateDiagram:
            """Generate a state diagram for a specific class."""
            # Check if class exists
            if class_name not in self.class_transitions:
                raise ValueError(f"Class {class_name} not found or has no state transitions")
            
            # Create the diagram
            diagram = StateDiagram(title=f"{class_name} State Diagram")
            
            # Add states from explicit annotations
            if class_name in self.class_states:
                for state_info in self.class_states[class_name].values():
                    state_type = (
                        StateType.INITIAL
                        if state_info.is_initial
                        else StateType.FINAL
                        if state_info.is_final
                        else StateType.NORMAL
                    )
                    
                    state = State(
                        id=state_info.state_id,
                        name=state_info.state_name,
                        type=state_type,
                        method_name=state_info.method_name,
                        line_number=state_info.line_number,
                        entry_actions=state_info.entry_actions,
                        exit_actions=state_info.exit_actions,
                    )
                    
                    diagram.add_state(state)
            
            # Add states from transitions
            transitions = self.class_transitions[class_name]
            
            # Track states found in transitions
            states_by_name: Dict[str, State] = {}
            
            # First pass: collect all states
            for transition in transitions:
                # Add source state if not already added
                if transition.source_state not in states_by_name:
                    state_id = f"state_{len(states_by_name)}"
                    state = State(
                        id=state_id,
                        name=transition.source_state,
                        method_name=transition.method_name,
                        line_number=transition.line_number,
                    )
                    states_by_name[transition.source_state] = state
                
                # Add target state if not already added
                if transition.target_state not in states_by_name:
                    state_id = f"state_{len(states_by_name)}"
                    state = State(
                        id=state_id,
                        name=transition.target_state,
                        method_name=transition.method_name,
                        line_number=transition.line_number,
                    )
                    states_by_name[transition.target_state] = state
            
            # Add all states to the diagram
            for state in states_by_name.values():
                diagram.add_state(state)
            
            # Add transitions
            for transition_info in transitions:
                source_id = states_by_name[transition_info.source_state].id
                target_id = states_by_name[transition_info.target_state].id
                
                transition = Transition(
                    source_id=source_id,
                    target_id=target_id,
                    event=transition_info.event,
                    guard=transition_info.guard,
                    action=transition_info.action,
                    method_name=transition_info.method_name,
                    line_number=transition_info.line_number,
                )
                
                diagram.add_transition(transition)
            
            return diagram

How the Analyzer Works
--------------------

The state analyzer works by:

1. **Detecting State Patterns**: It first identifies classes that use the state pattern by looking for a `state` field and state transitions.

2. **Extracting State Information**: It extracts state information from:
   - Explicit state field assignments (`self.state = "new_state"`)
   - State transition methods
   - Decorator-based state definitions (`@state("state_name")`)

3. **Building the State Diagram**: It builds a state diagram model with states and transitions.

The analyzer uses Python's AST module to parse and analyze Python code, making it possible to extract state patterns without executing the code.

Usage Example
-----------

Here's an example of how to use the state analyzer:

.. code-block:: python

    from pathlib import Path
    from utils.state_extractor import StateAnalyzer
    
    # Create analyzer
    analyzer = StateAnalyzer("./backend/app")
    
    # Analyze directory
    analyzer.analyze_directory()
    
    # Generate state diagram for a specific class
    diagram = analyzer.generate_state_diagram("Document")
    
    # Now you can use the diagram with a generator to create PlantUML

This will analyze all Python files in the `backend/app` directory, looking for classes that use the state pattern, and generate a state diagram for the `Document` class.