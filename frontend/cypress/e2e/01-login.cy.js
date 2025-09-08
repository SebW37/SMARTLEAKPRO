// Tests E2E - Connexion - Phase Test & Debug
describe('Connexion utilisateur', () => {
  beforeEach(() => {
    cy.visit('/')
  })

  it('Devrait afficher la page de connexion', () => {
    cy.get('h1').should('contain', 'Connexion')
    cy.get('input[name="nom_utilisateur"]').should('be.visible')
    cy.get('input[name="mot_de_passe"]').should('be.visible')
    cy.get('button[type="submit"]').should('be.visible')
  })

  it('Devrait afficher une erreur avec des identifiants invalides', () => {
    cy.get('input[name="nom_utilisateur"]').type('invalid_user')
    cy.get('input[name="mot_de_passe"]').type('wrong_password')
    cy.get('button[type="submit"]').click()
    
    cy.get('.alert-danger').should('be.visible')
    cy.get('.alert-danger').should('contain', 'Identifiants invalides')
  })

  it('Devrait se connecter avec des identifiants valides', () => {
    cy.get('input[name="nom_utilisateur"]').type(Cypress.env('testUser').username)
    cy.get('input[name="mot_de_passe"]').type(Cypress.env('testUser').password)
    cy.get('button[type="submit"]').click()
    
    // Vérifier la redirection vers le dashboard
    cy.url().should('include', '/dashboard')
    cy.get('h1').should('contain', 'Dashboard')
  })

  it('Devrait afficher le menu de navigation après connexion', () => {
    cy.login()
    
    cy.get('nav').should('be.visible')
    cy.get('nav').should('contain', 'Clients')
    cy.get('nav').should('contain', 'Interventions')
    cy.get('nav').should('contain', 'Planning')
    cy.get('nav').should('contain', 'Rapports')
    cy.get('nav').should('contain', 'Médias')
  })

  it('Devrait se déconnecter correctement', () => {
    cy.login()
    
    cy.get('button').contains('Déconnexion').click()
    
    // Vérifier la redirection vers la page de connexion
    cy.url().should('include', '/login')
    cy.get('h1').should('contain', 'Connexion')
  })
})
