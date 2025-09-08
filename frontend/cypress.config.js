// Configuration Cypress - Phase Test & Debug
const { defineConfig } = require('cypress')

module.exports = defineConfig({
  e2e: {
    baseUrl: 'http://localhost:3000',
    viewportWidth: 1280,
    viewportHeight: 720,
    video: true,
    screenshotOnRunFailure: true,
    defaultCommandTimeout: 10000,
    requestTimeout: 10000,
    responseTimeout: 10000,
    setupNodeEvents(on, config) {
      // Configuration des événements
      on('task', {
        log(message) {
          console.log(message)
          return null
        }
      })
    },
    env: {
      apiUrl: 'http://localhost:8000/api',
      testUser: {
        username: 'test_user',
        password: 'testpassword'
      }
    }
  },
  component: {
    devServer: {
      framework: 'create-react-app',
      bundler: 'webpack'
    }
  }
})
