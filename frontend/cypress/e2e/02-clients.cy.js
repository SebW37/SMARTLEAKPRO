// Tests E2E - Gestion des clients - Phase Test & Debug
describe('Gestion des clients', () => {
  beforeEach(() => {
    cy.login()
    cy.visit('/clients')
  })

  it('Devrait afficher la liste des clients', () => {
    cy.get('h1').should('contain', 'Clients')
    cy.get('table').should('be.visible')
    cy.get('thead').should('contain', 'Nom')
    cy.get('thead').should('contain', 'Email')
    cy.get('thead').should('contain', 'Téléphone')
    cy.get('thead').should('contain', 'Statut')
  })

  it('Devrait afficher le bouton de création de client', () => {
    cy.get('button').contains('Nouveau Client').should('be.visible')
  })

  it('Devrait ouvrir le formulaire de création de client', () => {
    cy.get('button').contains('Nouveau Client').click()
    
    cy.get('h2').should('contain', 'Nouveau Client')
    cy.get('input[name="nom"]').should('be.visible')
    cy.get('input[name="email"]').should('be.visible')
    cy.get('input[name="telephone"]').should('be.visible')
    cy.get('textarea[name="adresse"]').should('be.visible')
    cy.get('select[name="statut"]').should('be.visible')
  })

  it('Devrait créer un nouveau client', () => {
    cy.get('button').contains('Nouveau Client').click()
    
    cy.get('input[name="nom"]').type('Client Test E2E')
    cy.get('input[name="email"]').type('client.e2e@example.com')
    cy.get('input[name="telephone"]').type('0123456789')
    cy.get('textarea[name="adresse"]').type('123 Rue Test E2E, 75001 Paris')
    cy.get('select[name="statut"]').select('actif')
    
    cy.get('button[type="submit"]').click()
    
    // Vérifier la création
    cy.get('.alert-success').should('be.visible')
    cy.get('.alert-success').should('contain', 'Client créé avec succès')
    
    // Vérifier que le client apparaît dans la liste
    cy.get('table tbody').should('contain', 'Client Test E2E')
  })

  it('Devrait valider les champs obligatoires', () => {
    cy.get('button').contains('Nouveau Client').click()
    
    cy.get('button[type="submit"]').click()
    
    // Vérifier les messages d'erreur
    cy.get('.invalid-feedback').should('be.visible')
    cy.get('.invalid-feedback').should('contain', 'Ce champ est obligatoire')
  })

  it('Devrait valider le format de l\'email', () => {
    cy.get('button').contains('Nouveau Client').click()
    
    cy.get('input[name="nom"]').type('Client Test')
    cy.get('input[name="email"]').type('email_invalide')
    cy.get('input[name="telephone"]').type('0123456789')
    cy.get('textarea[name="adresse"]').type('123 Rue Test')
    cy.get('select[name="statut"]').select('actif')
    
    cy.get('button[type="submit"]').click()
    
    cy.get('.invalid-feedback').should('contain', 'Format d\'email invalide')
  })

  it('Devrait afficher les détails d\'un client', () => {
    // Supposer qu'il y a au moins un client dans la liste
    cy.get('table tbody tr').first().click()
    
    cy.get('h2').should('contain', 'Détails du client')
    cy.get('.card').should('be.visible')
  })

  it('Devrait modifier un client existant', () => {
    cy.get('table tbody tr').first().click()
    
    cy.get('button').contains('Modifier').click()
    
    cy.get('input[name="nom"]').clear().type('Client Modifié E2E')
    cy.get('button[type="submit"]').click()
    
    cy.get('.alert-success').should('contain', 'Client modifié avec succès')
  })

  it('Devrait supprimer un client', () => {
    cy.get('table tbody tr').first().click()
    
    cy.get('button').contains('Supprimer').click()
    
    // Confirmer la suppression
    cy.get('.modal').should('be.visible')
    cy.get('.modal').should('contain', 'Êtes-vous sûr de vouloir supprimer ce client ?')
    cy.get('.modal button').contains('Confirmer').click()
    
    cy.get('.alert-success').should('contain', 'Client supprimé avec succès')
  })

  it('Devrait rechercher des clients', () => {
    cy.get('input[placeholder*="Rechercher"]').type('Test')
    cy.get('button').contains('Rechercher').click()
    
    // Vérifier que les résultats de recherche s'affichent
    cy.get('table tbody tr').should('have.length.at.least', 1)
  })

  it('Devrait filtrer les clients par statut', () => {
    cy.get('select[name="statut_filter"]').select('actif')
    cy.get('button').contains('Filtrer').click()
    
    // Vérifier que seuls les clients actifs s'affichent
    cy.get('table tbody tr').each(($row) => {
      cy.wrap($row).should('contain', 'Actif')
    })
  })

  it('Devrait paginer les résultats', () => {
    // Supposer qu'il y a plus de 10 clients
    cy.get('.pagination').should('be.visible')
    cy.get('.pagination .page-item').should('have.length.at.least', 2)
    
    // Cliquer sur la page suivante
    cy.get('.pagination .page-item').contains('2').click()
    
    // Vérifier que la page a changé
    cy.get('.pagination .page-item.active').should('contain', '2')
  })
})
