State Management
================

This section covers state management patterns in the frontend application.

Server State
------------

TanStack Query
~~~~~~~~~~~~~~

Server state management using TanStack Query (formerly React Query):

.. code-block:: typescript

    // Query hook
    function useUser(userId: string) {
        return useQuery({
            queryKey: ['user', userId],
            queryFn: () => api.users.getUser(userId),
            staleTime: 5 * 60 * 1000, // 5 minutes
        })
    }

    // Mutation hook
    function useUpdateUser() {
        return useMutation({
            mutationFn: (data: UpdateUserDto) =>
                api.users.updateUser(data),
            onSuccess: () => {
                queryClient.invalidateQueries(['user'])
            },
        })
    }

Query Configuration
~~~~~~~~~~~~~~~~~~~

.. code-block:: typescript

    // Global configuration
    const queryClient = new QueryClient({
        defaultOptions: {
            queries: {
                staleTime: 60 * 1000, // 1 minute
                cacheTime: 5 * 60 * 1000, // 5 minutes
                retry: 1,
                refetchOnWindowFocus: false,
            },
        },
    })

Cache Management
~~~~~~~~~~~~~~~~

.. code-block:: typescript

    // Prefetching data
    await queryClient.prefetchQuery({
        queryKey: ['user', userId],
        queryFn: () => api.users.getUser(userId),
    })

    // Invalidating cache
    queryClient.invalidateQueries({
        queryKey: ['user'],
        exact: false,
    })

    // Updating cache
    queryClient.setQueryData(['user', userId], (old) => ({
        ...old,
        name: 'New Name',
    }))

Local State
-----------

React Hooks
~~~~~~~~~~~

Managing component-level state:

.. code-block:: typescript

    // Form state hook
    function useForm<T>(initialState: T) {
        const [values, setValues] = useState<T>(initialState)
        const [errors, setErrors] = useState<Record<keyof T, string>>({})

        const handleChange = (field: keyof T, value: T[keyof T]) => {
            setValues(prev => ({ ...prev, [field]: value }))
            // Clear error when field is modified
            if (errors[field]) {
                setErrors(prev => ({ ...prev, [field]: '' }))
            }
        }

        return { values, errors, handleChange, setErrors }
    }

Context API
~~~~~~~~~~~

Sharing state between components:

.. code-block:: typescript

    // Auth context
    interface AuthContextType {
        user: User | null
        login: (credentials: LoginDto) => Promise<void>
        logout: () => void
    }

    const AuthContext = createContext<AuthContextType>(null!)

    export function AuthProvider({ children }: { children: React.ReactNode }) {
        const [user, setUser] = useState<User | null>(null)

        const login = async (credentials: LoginDto) => {
            const response = await api.auth.login(credentials)
            setUser(response.user)
        }

        const logout = () => {
            setUser(null)
        }

        return (
            <AuthContext.Provider value={{ user, login, logout }}>
                {children}
            </AuthContext.Provider>
        )
    }

Custom Hooks
~~~~~~~~~~~~

Reusable state logic:

.. code-block:: typescript

    // Pagination hook
    function usePagination<T>({
        items,
        pageSize = 10,
    }: {
        items: T[]
        pageSize?: number
    }) {
        const [page, setPage] = useState(1)
        const totalPages = Math.ceil(items.length / pageSize)

        const paginatedItems = items.slice(
            (page - 1) * pageSize,
            page * pageSize
        )

        return {
            items: paginatedItems,
            page,
            setPage,
            totalPages,
            hasNext: page < totalPages,
            hasPrev: page > 1,
        }
    }

State Persistence
-----------------

Local Storage
~~~~~~~~~~~~~

Persisting state in browser storage:

.. code-block:: typescript

    // Storage hook
    function useLocalStorage<T>(key: string, initialValue: T) {
        const [storedValue, setStoredValue] = useState<T>(() => {
            try {
                const item = window.localStorage.getItem(key)
                return item ? JSON.parse(item) : initialValue
            } catch (error) {
                console.error(error)
                return initialValue
            }
        })

        const setValue = (value: T | ((val: T) => T)) => {
            try {
                const valueToStore =
                    value instanceof Function ? value(storedValue) : value
                setStoredValue(valueToStore)
                window.localStorage.setItem(key, JSON.stringify(valueToStore))
            } catch (error) {
                console.error(error)
            }
        }

        return [storedValue, setValue] as const
    }

State Synchronization
---------------------

WebSocket State
~~~~~~~~~~~~~~~

Real-time state updates:

.. code-block:: typescript

    // WebSocket hook
    function useWebSocketState<T>(
        url: string,
        initialState: T
    ) {
        const [state, setState] = useState<T>(initialState)
        const socket = useRef<WebSocket>()

        useEffect(() => {
            socket.current = new WebSocket(url)

            socket.current.onmessage = (event) => {
                const data = JSON.parse(event.data)
                setState(data)
            }

            return () => {
                socket.current?.close()
            }
        }, [url])

        return state
    }

State Updates
~~~~~~~~~~~~~

Optimistic updates:

.. code-block:: typescript

    // Optimistic mutation
    const mutation = useMutation({
        mutationFn: updateTodo,
        onMutate: async (newTodo) => {
            // Cancel outgoing refetches
            await queryClient.cancelQueries(['todos'])

            // Snapshot previous value
            const previousTodos = queryClient.getQueryData(['todos'])

            // Optimistically update
            queryClient.setQueryData(['todos'], (old: Todo[]) =>
                old.map(todo =>
                    todo.id === newTodo.id ? newTodo : todo
                )
            )

            return { previousTodos }
        },
        onError: (err, newTodo, context) => {
            // Rollback on error
            queryClient.setQueryData(
                ['todos'],
                context?.previousTodos
            )
        },
    })

Best Practices
--------------

1. State Organization
   * Separate local and server state
   * Use appropriate state management tools
   * Keep state close to where it's used

2. Performance
   * Minimize state updates
   * Use memoization
   * Batch updates when possible

3. Type Safety
   * Define state types
   * Use discriminated unions
   * Validate state changes

4. Error Handling
   * Handle loading states
   * Provide error states
   * Implement retry logic


