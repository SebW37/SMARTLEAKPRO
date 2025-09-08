// Commandes personnalisées Cypress - Phase Test & Debug

// Commande de connexion
Cypress.Commands.add('login', (username, password) => {
  const user = username || Cypress.env('testUser').username
  const pass = password || Cypress.env('testUser').password
  
  cy.visit('/login')
  cy.get('input[name="nom_utilisateur"]').type(user)
  cy.get('input[name="mot_de_passe"]').type(pass)
  cy.get('button[type="submit"]').click()
  
  // Attendre la redirection vers le dashboard
  cy.url().should('include', '/dashboard')
})

// Commande de déconnexion
Cypress.Commands.add('logout', () => {
  cy.get('button').contains('Déconnexion').click()
  cy.url().should('include', '/login')
})

// Commande pour attendre qu'un élément soit visible
Cypress.Commands.add('waitForElement', (selector, timeout = 10000) => {
  cy.get(selector, { timeout }).should('be.visible')
})

// Commande pour attendre qu'un élément disparaisse
Cypress.Commands.add('waitForElementToDisappear', (selector, timeout = 10000) => {
  cy.get(selector, { timeout }).should('not.exist')
})

// Commande pour vider un champ
Cypress.Commands.add('clearField', (selector) => {
  cy.get(selector).clear()
})

// Commande pour sélectionner une option dans un select
Cypress.Commands.add('selectOption', (selector, value) => {
  cy.get(selector).select(value)
})

// Commande pour vérifier qu'un message d'erreur s'affiche
Cypress.Commands.add('shouldShowError', (message) => {
  cy.get('.alert-danger').should('be.visible')
  cy.get('.alert-danger').should('contain', message)
})

// Commande pour vérifier qu'un message de succès s'affiche
Cypress.Commands.add('shouldShowSuccess', (message) => {
  cy.get('.alert-success').should('be.visible')
  cy.get('.alert-success').should('contain', message)
})

// Commande pour attendre qu'une requête API se termine
Cypress.Commands.add('waitForApi', (method, url) => {
  cy.intercept(method, url).as('apiCall')
  cy.wait('@apiCall')
})

// Commande pour intercepter les requêtes API
Cypress.Commands.add('interceptApi', (method, url, response) => {
  cy.intercept(method, url, response).as('apiCall')
})

// Commande pour vérifier qu'une requête API a été appelée
Cypress.Commands.add('shouldHaveCalledApi', (alias) => {
  cy.get(`@${alias}`).should('have.been.called')
})

// Commande pour vérifier le statut d'une requête API
Cypress.Commands.add('shouldHaveApiStatus', (alias, status) => {
  cy.get(`@${alias}`).its('response.statusCode').should('eq', status)
})

// Commande pour simuler un upload de fichier
Cypress.Commands.add('uploadFile', (selector, filePath, mimeType) => {
  cy.get(selector).selectFile(filePath, { force: true })
})

// Commande pour vérifier qu'un fichier a été uploadé
Cypress.Commands.add('shouldHaveUploadedFile', (fileName) => {
  cy.get('.file-list').should('contain', fileName)
})

// Commande pour attendre qu'une animation se termine
Cypress.Commands.add('waitForAnimation', (selector) => {
  cy.get(selector).should('not.have.class', 'animating')
})

// Commande pour vérifier qu'un modal s'ouvre
Cypress.Commands.add('shouldOpenModal', (title) => {
  cy.get('.modal').should('be.visible')
  cy.get('.modal').should('contain', title)
})

// Commande pour fermer un modal
Cypress.Commands.add('closeModal', () => {
  cy.get('.modal .btn-close').click()
  cy.get('.modal').should('not.exist')
})

// Commande pour vérifier qu'un tableau contient des données
Cypress.Commands.add('shouldHaveTableData', (tableSelector, minRows = 1) => {
  cy.get(tableSelector).find('tbody tr').should('have.length.at.least', minRows)
})

// Commande pour vérifier qu'un tableau est vide
Cypress.Commands.add('shouldHaveEmptyTable', (tableSelector) => {
  cy.get(tableSelector).find('tbody tr').should('have.length', 0)
  cy.get(tableSelector).should('contain', 'Aucune donnée')
})

// Commande pour vérifier qu'un formulaire est valide
Cypress.Commands.add('shouldHaveValidForm', (formSelector) => {
  cy.get(formSelector).find('.is-invalid').should('have.length', 0)
  cy.get(formSelector).find('.is-valid').should('have.length.at.least', 1)
})

// Commande pour vérifier qu'un formulaire est invalide
Cypress.Commands.add('shouldHaveInvalidForm', (formSelector) => {
  cy.get(formSelector).find('.is-invalid').should('have.length.at.least', 1)
})

// Commande pour vérifier qu'un bouton est désactivé
Cypress.Commands.add('shouldHaveDisabledButton', (buttonSelector) => {
  cy.get(buttonSelector).should('be.disabled')
})

// Commande pour vérifier qu'un bouton est activé
Cypress.Commands.add('shouldHaveEnabledButton', (buttonSelector) => {
  cy.get(buttonSelector).should('not.be.disabled')
})

// Commande pour vérifier qu'un élément a une classe CSS
Cypress.Commands.add('shouldHaveClass', (selector, className) => {
  cy.get(selector).should('have.class', className)
})

// Commande pour vérifier qu'un élément n'a pas une classe CSS
Cypress.Commands.add('shouldNotHaveClass', (selector, className) => {
  cy.get(selector).should('not.have.class', className)
})

// Commande pour vérifier qu'un élément a un attribut
Cypress.Commands.add('shouldHaveAttribute', (selector, attribute, value) => {
  cy.get(selector).should('have.attr', attribute, value)
})

// Commande pour vérifier qu'un élément n'a pas un attribut
Cypress.Commands.add('shouldNotHaveAttribute', (selector, attribute) => {
  cy.get(selector).should('not.have.attr', attribute)
})

// Commande pour vérifier qu'un élément contient du texte
Cypress.Commands.add('shouldContainText', (selector, text) => {
  cy.get(selector).should('contain', text)
})

// Commande pour vérifier qu'un élément ne contient pas de texte
Cypress.Commands.add('shouldNotContainText', (selector, text) => {
  cy.get(selector).should('not.contain', text)
})

// Commande pour vérifier qu'un élément est visible
Cypress.Commands.add('shouldBeVisible', (selector) => {
  cy.get(selector).should('be.visible')
})

// Commande pour vérifier qu'un élément n'est pas visible
Cypress.Commands.add('shouldNotBeVisible', (selector) => {
  cy.get(selector).should('not.be.visible')
})

// Commande pour vérifier qu'un élément existe
Cypress.Commands.add('shouldExist', (selector) => {
  cy.get(selector).should('exist')
})

// Commande pour vérifier qu'un élément n'existe pas
Cypress.Commands.add('shouldNotExist', (selector) => {
  cy.get(selector).should('not.exist')
})

// Commande pour vérifier qu'un élément est en focus
Cypress.Commands.add('shouldBeFocused', (selector) => {
  cy.get(selector).should('be.focused')
})

// Commande pour vérifier qu'un élément n'est pas en focus
Cypress.Commands.add('shouldNotBeFocused', (selector) => {
  cy.get(selector).should('not.be.focused')
})

// Commande pour vérifier qu'un élément est sélectionné
Cypress.Commands.add('shouldBeSelected', (selector) => {
  cy.get(selector).should('be.checked')
})

// Commande pour vérifier qu'un élément n'est pas sélectionné
Cypress.Commands.add('shouldNotBeSelected', (selector) => {
  cy.get(selector).should('not.be.checked')
})

// Commande pour vérifier qu'un élément a une valeur
Cypress.Commands.add('shouldHaveValue', (selector, value) => {
  cy.get(selector).should('have.value', value)
})

// Commande pour vérifier qu'un élément n'a pas une valeur
Cypress.Commands.add('shouldNotHaveValue', (selector, value) => {
  cy.get(selector).should('not.have.value', value)
})

// Commande pour vérifier qu'un élément a un texte
Cypress.Commands.add('shouldHaveText', (selector, text) => {
  cy.get(selector).should('have.text', text)
})

// Commande pour vérifier qu'un élément n'a pas un texte
Cypress.Commands.add('shouldNotHaveText', (selector, text) => {
  cy.get(selector).should('not.have.text', text)
})

// Commande pour vérifier qu'un élément a une longueur
Cypress.Commands.add('shouldHaveLength', (selector, length) => {
  cy.get(selector).should('have.length', length)
})

// Commande pour vérifier qu'un élément a une longueur minimale
Cypress.Commands.add('shouldHaveMinLength', (selector, minLength) => {
  cy.get(selector).should('have.length.at.least', minLength)
})

// Commande pour vérifier qu'un élément a une longueur maximale
Cypress.Commands.add('shouldHaveMaxLength', (selector, maxLength) => {
  cy.get(selector).should('have.length.at.most', maxLength)
})
