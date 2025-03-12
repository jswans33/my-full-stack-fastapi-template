Testing Guide
=============

This section covers testing strategies and practices for the frontend application.

Testing Stack
-------------

Core Tools
~~~~~~~~~~

* Playwright - End-to-end testing
* Testing Library - Component testing
* Vitest - Unit testing
* MSW - API mocking

Configuration
~~~~~~~~~~~~~

.. code-block:: typescript

    // playwright.config.ts
    import { defineConfig } from '@playwright/test'

    export default defineConfig({
        testDir: './tests',
        use: {
            baseURL: 'http://localhost:3000',
            screenshot: 'only-on-failure',
        },
        projects: [
            {
                name: 'chromium',
                use: { browserName: 'chromium' },
            },
        ],
    })

Component Testing
-----------------

Basic Tests
~~~~~~~~~~~

.. code-block:: typescript

    // Button.test.tsx
    import { render, screen } from '@testing-library/react'
    import userEvent from '@testing-library/user-event'
    import { Button } from './Button'

    test('calls onClick when clicked', async () => {
        const onClick = vi.fn()
        render(<Button onClick={onClick}>Click Me</Button>)

        await userEvent.click(screen.getByText('Click Me'))
        expect(onClick).toHaveBeenCalled()
    })

Custom Renders
~~~~~~~~~~~~~~

.. code-block:: typescript

    // test-utils.tsx
    import { render as rtlRender } from '@testing-library/react'
    import { QueryClient, QueryClientProvider } from '@tanstack/react-query'

    function render(ui: React.ReactElement, options = {}) {
        const queryClient = new QueryClient({
            defaultOptions: {
                queries: {
                    retry: false,
                },
            },
        })

        return rtlRender(ui, {
            wrapper: ({ children }) => (
                <QueryClientProvider client={queryClient}>
                    {children}
                </QueryClientProvider>
            ),
            ...options,
        })
    }

    export * from '@testing-library/react'
    export { render }

Integration Testing
-------------------

API Mocking
~~~~~~~~~~~

.. code-block:: typescript

    // handlers.ts
    import { rest } from 'msw'

    export const handlers = [
        rest.get('/api/users', (req, res, ctx) => {
            return res(
                ctx.json([
                    { id: 1, name: 'John' },
                    { id: 2, name: 'Jane' },
                ])
            )
        }),
    ]

    // setupTests.ts
    import { setupServer } from 'msw/node'
    import { handlers } from './handlers'

    const server = setupServer(...handlers)

    beforeAll(() => server.listen())
    afterEach(() => server.resetHandlers())
    afterAll(() => server.close())

Testing Hooks
~~~~~~~~~~~~~

.. code-block:: typescript

    // useUser.test.ts
    import { renderHook, waitFor } from '@testing-library/react'
    import { useUser } from './useUser'

    test('fetches user data', async () => {
        const { result } = renderHook(() => useUser('123'))

        await waitFor(() => {
            expect(result.current.isSuccess).toBe(true)
        })

        expect(result.current.data).toEqual({
            id: '123',
            name: 'John',
        })
    })

End-to-End Testing
------------------

Page Objects
~~~~~~~~~~~~

.. code-block:: typescript

    // LoginPage.ts
    export class LoginPage {
        constructor(private page: Page) {}

        async goto() {
            await this.page.goto('/login')
        }

        async login(email: string, password: string) {
            await this.page.fill('[name="email"]', email)
            await this.page.fill('[name="password"]', password)
            await this.page.click('button[type="submit"]')
        }

        async getErrorMessage() {
            return this.page.textContent('.error-message')
        }
    }

Test Scenarios
~~~~~~~~~~~~~~

.. code-block:: typescript

    // login.spec.ts
    import { test, expect } from '@playwright/test'
    import { LoginPage } from './LoginPage'

    test('successful login', async ({ page }) => {
        const loginPage = new LoginPage(page)
        await loginPage.goto()
        await loginPage.login('user@example.com', 'password')

        await expect(page).toHaveURL('/dashboard')
    })

    test('invalid credentials', async ({ page }) => {
        const loginPage = new LoginPage(page)
        await loginPage.goto()
        await loginPage.login('invalid@example.com', 'wrong')

        const error = await loginPage.getErrorMessage()
        expect(error).toBe('Invalid credentials')
    })

Visual Testing
--------------

Screenshot Tests
~~~~~~~~~~~~~~~~

.. code-block:: typescript

    // visual.spec.ts
    import { test, expect } from '@playwright/test'

    test('dashboard layout', async ({ page }) => {
        await page.goto('/dashboard')
        await expect(page).toHaveScreenshot('dashboard.png')
    })

    test('dark mode', async ({ page }) => {
        await page.goto('/dashboard')
        await page.click('[data-testid="theme-toggle"]')
        await expect(page).toHaveScreenshot('dashboard-dark.png')
    })

Performance Testing
-------------------

Metrics Collection
~~~~~~~~~~~~~~~~~~

.. code-block:: typescript

    // performance.spec.ts
    import { test, expect } from '@playwright/test'

    test('page load performance', async ({ page }) => {
        const startTime = Date.now()
        await page.goto('/dashboard')
        const loadTime = Date.now() - startTime

        expect(loadTime).toBeLessThan(2000)
    })

Test Coverage
-------------

Coverage Configuration
~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: typescript

    // vitest.config.ts
    import { defineConfig } from 'vitest/config'

    export default defineConfig({
        test: {
            coverage: {
                reporter: ['text', 'json', 'html'],
                exclude: [
                    'node_modules/',
                    'test/',
                    '**/*.test.ts',
                ],
            },
        },
    })

Best Practices
--------------

1. Test Organization
   * Group related tests
   * Use descriptive names
   * Follow AAA pattern (Arrange, Act, Assert)

2. Test Isolation
   * Reset state between tests
   * Mock external dependencies
   * Clean up after tests

3. Test Coverage
   * Test critical paths
   * Include edge cases
   * Test error scenarios

4. Test Maintenance
   * Keep tests simple
   * Avoid test duplication
   * Update tests with code changes
