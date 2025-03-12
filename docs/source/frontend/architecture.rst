Frontend Architecture
=====================

This section covers the architectural design of the frontend application.

Overview
--------

The frontend is built with modern React and follows a component-based architecture:

.. code-block:: text

    frontend/
    ├── src/
    │   ├── components/     # Reusable UI components
    │   ├── hooks/         # Custom React hooks
    │   ├── routes/        # Application routes
    │   ├── client/        # Auto-generated API client
    │   └── theme/         # UI theme configuration

Component Architecture
----------------------

Component Types
---------------

1. Page Components
   * Route-level components
   * Handle data fetching
   * Manage page state

2. Feature Components
   * Complex UI features
   * Business logic
   * State management

3. Common Components
   * Reusable UI elements
   * Presentation focused
   * Minimal logic

Component Structure
-------------------

.. code-block:: js

    // Example component structure
    import { FC } from 'react'
    import { useQuery } from '@tanstack/react-query'
    import { Box, Heading } from '@chakra-ui/react'

    interface Props {
        userId: string
    }

    export const UserProfile: FC<Props> = ({ userId }) => {
        const { data, isLoading } = useQuery(['user', userId], () =>
            api.users.getUser(userId)
        )

        if (isLoading) return <Loading />

        return (
            <Box>
                <Heading>{data.name}</Heading>
                {/* Component content */}
            </Box>
        )
    }

Routing Architecture
--------------------

TanStack Router
---------------

.. code-block:: js

    // Route definition
    import { createRoute } from '@tanstack/react-router'

    export const userRoute = createRoute({
        getParentRoute: () => rootRoute,
        path: 'users/$userId',
        component: UserProfilePage,
        loader: ({ params }) => {
            return queryClient.ensureQueryData({
                queryKey: ['user', params.userId],
                queryFn: () => api.users.getUser(params.userId),
            })
        },
    })

Route Structure
---------------

.. mermaid::

    graph TD
        A[Root Layout] --> B[Public Routes]
        A --> C[Protected Routes]
        B --> D[Login]
        B --> E[Sign Up]
        B --> F[Password Reset]
        C --> G[Dashboard]
        C --> H[User Settings]
        C --> I[Admin Panel]

State Management
----------------

1. Server State
---------------

Using TanStack Query:

.. code-block:: js

    // Query hook
    function useUser(userId: string) {
        return useQuery({
            queryKey: ['user', userId],
            queryFn: () => api.users.getUser(userId),
            staleTime: 5 * 60 * 1000,
        })
    }

2. Local State
--------------

Using React hooks:

.. code-block:: js

    // Local state hook
    function useFormState<T>(initial: T) {
        const [data, setData] = useState<T>(initial)
        const [errors, setErrors] = useState<Record<keyof T, string>>({})

        return {
            data,
            errors,
            setField: (field: keyof T, value: T[keyof T]) => {
                setData(prev => ({ ...prev, [field]: value }))
            },
            setError: (field: keyof T, message: string) => {
                setErrors(prev => ({ ...prev, [field]: message }))
            },
        }
    }

API Integration
---------------

Auto-generated Client
---------------------

.. code-block:: js

    // Using generated API client
    import { api } from '@/client'

    async function createUser(data: CreateUserDto) {
        const response = await api.users.createUser(data)
        return response.data
    }

Error Handling
--------------

.. code-block:: js

    // API error handling
    import { ApiError } from '@/client'

    try {
        await api.users.createUser(data)
    } catch (error) {
        if (error instanceof ApiError) {
            // Handle API error
            console.error(error.status, error.message)
        } else {
            // Handle other errors
            console.error('Unknown error:', error)
        }
    }

Theme System
------------

Chakra UI Theme
---------------

.. code-block:: js

    // Theme configuration
    import { extendTheme } from '@chakra-ui/react'

    export const theme = extendTheme({
        colors: {
            brand: {
                50: '#f7fafc',
                // ... other shades
                900: '#1a202c',
            },
        },
        components: {
            Button: {
                variants: {
                    primary: {
                        bg: 'brand.500',
                        color: 'white',
                    },
                },
            },
        },
    })

Dark Mode
---------

.. code-block:: js

    // Dark mode hook
    export function useDarkMode() {
        const { colorMode, toggleColorMode } = useColorMode()

        return {
            isDark: colorMode === 'dark',
            toggle: toggleColorMode,
        }
    }

Performance Optimization
------------------------

1. Code Splitting
-----------------

.. code-block:: js

    // Lazy loading components
    const AdminPanel = lazy(() => import('./AdminPanel'))

2. Memoization
--------------

.. code-block:: js

    // Memoized component
    const MemoizedComponent = memo(({ data }) => (
        <Box>{data.map(renderItem)}</Box>
    ))

3. Virtual Lists
----------------

.. code-block:: js

    // Virtual list for large datasets
    import { VirtualList } from '@/components/VirtualList'

    function LargeList({ items }) {
        return (
            <VirtualList
                height={400}
                itemCount={items.length}
                itemSize={50}
                renderItem={({ index }) => (
                    <ListItem item={items[index]} />
                )}
            />
        )
    }

Development Tools
-----------------

1. TypeScript Configuration
---------------------------

.. code-block:: js

    // tsconfig.json
    {
        "compilerOptions": {
            "target": "ES2020",
            "lib": ["DOM", "DOM.Iterable", "ES2020"],
            "strict": true,
            "paths": {
                "@/*": ["./src/*"]
            }
        }
    }

2. Build Configuration
----------------------

.. code-block:: js

    // vite.config.ts
    export default defineConfig({
        plugins: [react()],
        resolve: {
            alias: {
                '@': '/src'
            }
        },
        build: {
            sourcemap: true,
            chunkSizeWarningLimit: 1000
        }
    })


