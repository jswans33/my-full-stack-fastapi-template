Routing System
==============

This section covers the routing system implemented using TanStack Router.

Route Configuration
-------------------

Basic Setup
~~~~~~~~~~~

.. code-block:: typescript

    // src/routeTree.gen.ts
    import { createRouteConfig } from '@tanstack/react-router'

    export const routeConfig = createRouteConfig({
        component: RootLayout,
        children: [
            {
                path: '/',
                component: HomePage,
            },
            {
                path: 'login',
                component: LoginPage,
            },
            {
                path: 'dashboard',
                component: DashboardPage,
                loader: () => requireAuth(),
            },
        ],
    })

Protected Routes
~~~~~~~~~~~~~~~~

.. code-block:: typescript

    // src/utils/auth.ts
    export function requireAuth() {
        const auth = useAuth()
        if (!auth.isAuthenticated) {
            throw redirect({
                to: '/login',
                search: {
                    redirect: window.location.pathname,
                },
            })
        }
    }

Route Parameters
----------------

Dynamic Routes
~~~~~~~~~~~~~~

.. code-block:: typescript

    // User profile route
    {
        path: 'users/$userId',
        component: UserProfilePage,
        loader: ({ params }) => {
            return queryClient.ensureQueryData({
                queryKey: ['user', params.userId],
                queryFn: () => api.users.getUser(params.userId),
            })
        },
    }

Optional Parameters
~~~~~~~~~~~~~~~~~~~

.. code-block:: typescript

    // Search route with optional filters
    {
        path: 'search',
        component: SearchPage,
        validateSearch: (search: Record<string, unknown>) => ({
            query: search.query as string,
            category: search.category as string | undefined,
            page: Number(search.page) || 1,
        }),
    }

Route Loaders
-------------

Data Loading
~~~~~~~~~~~~

.. code-block:: typescript

    // Route with data loader
    {
        path: 'items/$itemId',
        component: ItemDetailPage,
        loader: async ({ params }) => {
            const item = await queryClient.ensureQueryData({
                queryKey: ['item', params.itemId],
                queryFn: () => api.items.getItem(params.itemId),
            })
            return { item }
        },
    }

Error Handling
~~~~~~~~~~~~~~

.. code-block:: typescript

    // Error boundary for routes
    {
        path: 'items/$itemId',
        component: ItemDetailPage,
        errorComponent: ItemErrorBoundary,
        loader: async ({ params }) => {
            try {
                const item = await api.items.getItem(params.itemId)
                return { item }
            } catch (error) {
                throw new Error('Failed to load item')
            }
        },
    }

Navigation
----------

Link Component
~~~~~~~~~~~~~~

.. code-block:: typescript

    import { Link } from '@tanstack/react-router'

    function Navigation() {
        return (
            <nav>
                <Link to="/">Home</Link>
                <Link to="/dashboard">Dashboard</Link>
                <Link
                    to="/users/$userId"
                    params={{ userId: '123' }}
                >
                    User Profile
                </Link>
            </nav>
        )
    }

Programmatic Navigation
~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: typescript

    import { useNavigate } from '@tanstack/react-router'

    function LoginForm() {
        const navigate = useNavigate()

        const onSuccess = () => {
            navigate({
                to: '/dashboard',
                replace: true,
            })
        }
    }

Route Guards
------------

Authentication Guard
~~~~~~~~~~~~~~~~~~~~

.. code-block:: typescript

    function AuthGuard({ children }: { children: React.ReactNode }) {
        const auth = useAuth()
        const navigate = useNavigate()

        useEffect(() => {
            if (!auth.isAuthenticated) {
                navigate({
                    to: '/login',
                    search: {
                        redirect: window.location.pathname,
                    },
                })
            }
        }, [auth.isAuthenticated])

        return auth.isAuthenticated ? children : null
    }

Role Guard
~~~~~~~~~~

.. code-block:: typescript

    function RoleGuard({
        children,
        requiredRole,
    }: {
        children: React.ReactNode
        requiredRole: string
    }) {
        const auth = useAuth()

        if (!auth.user?.roles.includes(requiredRole)) {
            return <AccessDenied />
        }

        return children
    }

Route Layouts
-------------

Nested Layouts
~~~~~~~~~~~~~~

.. code-block:: typescript

    // Base layout
    function RootLayout() {
        return (
            <div>
                <Header />
                <Outlet />
                <Footer />
            </div>
        )
    }

    // Dashboard layout
    function DashboardLayout() {
        return (
            <div className="dashboard-layout">
                <Sidebar />
                <main>
                    <Outlet />
                </main>
            </div>
        )
    }

Route Context
-------------

Sharing Data
~~~~~~~~~~~~

.. code-block:: typescript

    // Create route context
    const DashboardContext = createContext<DashboardContextType>(null!)

    // Route with context
    function DashboardRoute() {
        const dashboardData = useDashboardData()

        return (
            <DashboardContext.Provider value={dashboardData}>
                <Outlet />
            </DashboardContext.Provider>
        )
    }

Route Transitions
-----------------

Loading States
~~~~~~~~~~~~~~

.. code-block:: typescript

    function RouteLoadingIndicator() {
        const navigation = useNavigation()

        if (navigation.state === 'loading') {
            return <LoadingSpinner />
        }

        return null
    }

Animations
~~~~~~~~~~

.. code-block:: typescript

    import { motion } from 'framer-motion'

    function PageTransition({ children }: { children: React.ReactNode }) {
        return (
            <motion.div
                initial={{ opacity: 0 }}
                animate={{ opacity: 1 }}
                exit={{ opacity: 0 }}
            >
                {children}
            </motion.div>
        )
    }

Best Practices
--------------

1. Route Organization
   * Group related routes
   * Use consistent naming
   * Keep routes shallow

2. Performance
   * Use code splitting
   * Preload critical routes
   * Cache route data

3. Error Handling
   * Provide error boundaries
   * Handle 404 routes
   * Show loading states

4. Type Safety
   * Use TypeScript
   * Validate route params
   * Type route context


