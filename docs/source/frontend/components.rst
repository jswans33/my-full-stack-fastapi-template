Component Library
=================

This section documents the reusable components available in the frontend application.

Component Categories
--------------------

Common Components
~~~~~~~~~~~~~~~~~

Basic UI elements used throughout the application:

.. code-block:: typescript

    // Button component
    import { Button as ChakraButton } from '@chakra-ui/react'

    interface ButtonProps {
        variant?: 'solid' | 'outline' | 'ghost'
        size?: 'sm' | 'md' | 'lg'
        isLoading?: boolean
        children: React.ReactNode
    }

    export const Button: React.FC<ButtonProps> = ({
        variant = 'solid',
        size = 'md',
        isLoading,
        children,
        ...props
    }) => (
        <ChakraButton
            variant={variant}
            size={size}
            isLoading={isLoading}
            {...props}
        >
            {children}
        </ChakraButton>
    )

Form Components
~~~~~~~~~~~~~~~

Form-specific components with validation:

.. code-block:: typescript

    // FormField component
    import { FormControl, FormLabel, Input, FormErrorMessage } from '@chakra-ui/react'

    interface FormFieldProps {
        label: string
        name: string
        type?: string
        error?: string
        value: string
        onChange: (e: React.ChangeEvent<HTMLInputElement>) => void
    }

    export const FormField: React.FC<FormFieldProps> = ({
        label,
        name,
        type = 'text',
        error,
        value,
        onChange,
    }) => (
        <FormControl isInvalid={!!error}>
            <FormLabel htmlFor={name}>{label}</FormLabel>
            <Input
                id={name}
                name={name}
                type={type}
                value={value}
                onChange={onChange}
            />
            {error && <FormErrorMessage>{error}</FormErrorMessage>}
        </FormControl>
    )

Layout Components
~~~~~~~~~~~~~~~~~

Components for page structure:

.. code-block:: typescript

    // PageLayout component
    import { Box, Container } from '@chakra-ui/react'

    interface PageLayoutProps {
        children: React.ReactNode
        maxWidth?: string
    }

    export const PageLayout: React.FC<PageLayoutProps> = ({
        children,
        maxWidth = '1200px'
    }) => (
        <Box minH="100vh" bg="gray.50">
            <Container maxW={maxWidth} py={8}>
                {children}
            </Container>
        </Box>
    )

Data Display Components
~~~~~~~~~~~~~~~~~~~~~~~

Components for displaying data:

.. code-block:: typescript

    // DataTable component
    import { Table, Thead, Tbody, Tr, Th, Td } from '@chakra-ui/react'

    interface Column<T> {
        key: keyof T
        header: string
        render?: (value: T[keyof T], item: T) => React.ReactNode
    }

    interface DataTableProps<T> {
        data: T[]
        columns: Column<T>[]
    }

    export function DataTable<T>({ data, columns }: DataTableProps<T>) {
        return (
            <Table>
                <Thead>
                    <Tr>
                        {columns.map(col => (
                            <Th key={col.key as string}>{col.header}</Th>
                        ))}
                    </Tr>
                </Thead>
                <Tbody>
                    {data.map((item, i) => (
                        <Tr key={i}>
                            {columns.map(col => (
                                <Td key={col.key as string}>
                                    {col.render
                                        ? col.render(item[col.key], item)
                                        : item[col.key]}
                                </Td>
                            ))}
                        </Tr>
                    ))}
                </Tbody>
            </Table>
        )
    }

Feedback Components
~~~~~~~~~~~~~~~~~~~

Components for user feedback:

.. code-block:: typescript

    // Alert component
    import { Alert as ChakraAlert, AlertIcon } from '@chakra-ui/react'

    interface AlertProps {
        type: 'info' | 'warning' | 'success' | 'error'
        message: string
    }

    export const Alert: React.FC<AlertProps> = ({ type, message }) => (
        <ChakraAlert status={type}>
            <AlertIcon />
            {message}
        </ChakraAlert>
    )

Navigation Components
~~~~~~~~~~~~~~~~~~~~~

Components for navigation:

.. code-block:: typescript

    // Sidebar component
    import { Box, VStack, Link } from '@chakra-ui/react'
    import { Link as RouterLink } from '@tanstack/react-router'

    interface NavItem {
        label: string
        path: string
        icon?: React.ReactNode
    }

    interface SidebarProps {
        items: NavItem[]
    }

    export const Sidebar: React.FC<SidebarProps> = ({ items }) => (
        <Box w="240px" bg="white" p={4} borderRight="1px" borderColor="gray.200">
            <VStack spacing={2} align="stretch">
                {items.map(item => (
                    <Link
                        key={item.path}
                        as={RouterLink}
                        to={item.path}
                        p={2}
                        _hover={{ bg: 'gray.100' }}
                    >
                        {item.icon && <Box mr={2}>{item.icon}</Box>}
                        {item.label}
                    </Link>
                ))}
            </VStack>
        </Box>
    )

Modal Components
~~~~~~~~~~~~~~~~

Reusable modal dialogs:

.. code-block:: typescript

    // ConfirmDialog component
    import {
        Modal,
        ModalOverlay,
        ModalContent,
        ModalHeader,
        ModalBody,
        ModalFooter,
        Button
    } from '@chakra-ui/react'

    interface ConfirmDialogProps {
        isOpen: boolean
        onClose: () => void
        onConfirm: () => void
        title: string
        message: string
    }

    export const ConfirmDialog: React.FC<ConfirmDialogProps> = ({
        isOpen,
        onClose,
        onConfirm,
        title,
        message
    }) => (
        <Modal isOpen={isOpen} onClose={onClose}>
            <ModalOverlay />
            <ModalContent>
                <ModalHeader>{title}</ModalHeader>
                <ModalBody>{message}</ModalBody>
                <ModalFooter>
                    <Button variant="ghost" mr={3} onClick={onClose}>
                        Cancel
                    </Button>
                    <Button colorScheme="red" onClick={onConfirm}>
                        Confirm
                    </Button>
                </ModalFooter>
            </ModalContent>
        </Modal>
    )

Component Usage
---------------

Component Props
~~~~~~~~~~~~~~~

All components should:

* Use TypeScript interfaces for props
* Document all props with JSDoc comments
* Provide sensible defaults
* Use proper type constraints

Example:

.. code-block:: typescript

    interface Props {
        /** The title to display */
        title: string
        /** Optional description */
        description?: string
        /** Click handler */
        onClick?: () => void
        /** Component children */
        children: React.ReactNode
    }

Component Best Practices
~~~~~~~~~~~~~~~~~~~~~~~~

1. Composition
   * Use composition over inheritance
   * Break down complex components
   * Create reusable hooks

2. Performance
   * Memoize when needed
   * Avoid unnecessary renders
   * Use proper dependencies

3. Accessibility
   * Include ARIA attributes
   * Support keyboard navigation
   * Test with screen readers

4. Error Handling
   * Use error boundaries
   * Provide fallback UI
   * Log errors appropriately

Component Testing
-----------------

Unit Tests
~~~~~~~~~~

.. code-block:: typescript

    import { render, screen } from '@testing-library/react'
    import userEvent from '@testing-library/user-event'
    import { Button } from './Button'

    test('calls onClick when clicked', async () => {
        const onClick = jest.fn()
        render(<Button onClick={onClick}>Click Me</Button>)

        await userEvent.click(screen.getByText('Click Me'))
        expect(onClick).toHaveBeenCalled()
    })

Integration Tests
~~~~~~~~~~~~~~~~~

.. code-block:: typescript

    import { render, screen } from '@testing-library/react'
    import { Form } from './Form'

    test('submits form data', async () => {
        const onSubmit = jest.fn()
        render(<Form onSubmit={onSubmit} />)

        await userEvent.type(
            screen.getByLabelText('Email'),
            'test@example.com'
        )
        await userEvent.click(screen.getByText('Submit'))

        expect(onSubmit).toHaveBeenCalledWith({
            email: 'test@example.com'
        })
    })

