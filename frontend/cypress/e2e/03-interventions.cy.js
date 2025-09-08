// Tests E2E - Gestion des interventions - Phase Test & Debug
describe('Gestion des interventions', () => {
  beforeEach(() => {
    cy.login()
    cy.visit('/interventions')
  })

  it('Devrait afficher la liste des interventions', () => {
    cy.get('h1').should('contain', 'Interventions')
    cy.get('table').should('be.visible')
    cy.get('thead').should('contain', 'Client')
    cy.get('thead').should('contain', 'Date')
    cy.get('thead').should('contain', 'Type')
    cy.get('thead').should('contain', 'Statut')
    cy.get('thead').should('contain', 'Lieu')
  })

  it('Devrait créer une nouvelle intervention', () => {
    cy.get('button').contains('Nouvelle Intervention').click()
    
    cy.get('h2').should('contain', 'Nouvelle Intervention')
    
    // Remplir le formulaire
    cy.get('select[name="client_id"]').select(1) // Sélectionner le premier client
    cy.get('input[name="date_intervention"]').type('2024-12-31T10:00')
    cy.get('select[name="type_intervention"]').select('inspection')
    cy.get('select[name="statut"]').select('planifie')
    cy.get('input[name="lieu"]').type('123 Rue Test, 75001 Paris')
    cy.get('textarea[name="description"]').type('Intervention de test E2E')
    
    cy.get('button[type="submit"]').click()
    
    cy.get('.alert-success').should('contain', 'Intervention créée avec succès')
  })

  it('Devrait changer le statut d\'une intervention', () => {
    // Supposer qu'il y a au moins une intervention
    cy.get('table tbody tr').first().click()
    
    cy.get('h2').should('contain', 'Détails de l\'intervention')
    
    // Changer le statut
    cy.get('select[name="statut"]').select('en_cours')
    cy.get('button').contains('Mettre à jour').click()
    
    cy.get('.alert-success').should('contain', 'Statut changé avec succès')
    
    // Vérifier que le statut a été mis à jour
    cy.get('select[name="statut"]').should('have.value', 'en_cours')
  })

  it('Devrait afficher les statistiques des interventions', () => {
    cy.get('.stats-cards').should('be.visible')
    cy.get('.stats-cards').should('contain', 'Total')
    cy.get('.stats-cards').should('contain', 'Planifiées')
    cy.get('.stats-cards').should('contain', 'En cours')
    cy.get('.stats-cards').should('contain', 'Validées')
  })

  it('Devrait filtrer les interventions par statut', () => {
    cy.get('select[name="statut_filter"]').select('planifie')
    cy.get('button').contains('Filtrer').click()
    
    // Vérifier que seules les interventions planifiées s'affichent
    cy.get('table tbody tr').each(($row) => {
      cy.wrap($row).should('contain', 'Planifié')
    })
  })

  it('Devrait filtrer les interventions par type', () => {
    cy.get('select[name="type_filter"]').select('inspection')
    cy.get('button').contains('Filtrer').click()
    
    // Vérifier que seules les inspections s'affichent
    cy.get('table tbody tr').each(($row) => {
      cy.wrap($row).should('contain', 'Inspection')
    })
  })

  it('Devrait filtrer les interventions par date', () => {
    const today = new Date().toISOString().split('T')[0]
    
    cy.get('input[name="date_debut"]').type(today)
    cy.get('input[name="date_fin"]').type(today)
    cy.get('button').contains('Filtrer').click()
    
    // Vérifier que les interventions du jour s'affichent
    cy.get('table tbody tr').should('have.length.at.least', 1)
  })

  it('Devrait rechercher des interventions', () => {
    cy.get('input[placeholder*="Rechercher"]').type('test')
    cy.get('button').contains('Rechercher').click()
    
    // Vérifier que les résultats de recherche s'affichent
    cy.get('table tbody tr').should('have.length.at.least', 1)
  })

  it('Devrait afficher les détails d\'une intervention', () => {
    cy.get('table tbody tr').first().click()
    
    cy.get('h2').should('contain', 'Détails de l\'intervention')
    cy.get('.card').should('be.visible')
    cy.get('.card').should('contain', 'Client')
    cy.get('.card').should('contain', 'Date')
    cy.get('.card').should('contain', 'Type')
    cy.get('.card').should('contain', 'Statut')
    cy.get('.card').should('contain', 'Lieu')
    cy.get('.card').should('contain', 'Description')
  })

  it('Devrait modifier une intervention existante', () => {
    cy.get('table tbody tr').first().click()
    
    cy.get('button').contains('Modifier').click()
    
    cy.get('input[name="lieu"]').clear().type('Nouveau lieu E2E')
    cy.get('textarea[name="description"]').clear().type('Description modifiée E2E')
    
    cy.get('button[type="submit"]').click()
    
    cy.get('.alert-success').should('contain', 'Intervention modifiée avec succès')
  })

  it('Devrait supprimer une intervention', () => {
    cy.get('table tbody tr').first().click()
    
    cy.get('button').contains('Supprimer').click()
    
    // Confirmer la suppression
    cy.get('.modal').should('be.visible')
    cy.get('.modal').should('contain', 'Êtes-vous sûr de vouloir supprimer cette intervention ?')
    cy.get('.modal button').contains('Confirmer').click()
    
    cy.get('.alert-success').should('contain', 'Intervention supprimée avec succès')
  })

  it('Devrait afficher les médias d\'une intervention', () => {
    cy.get('table tbody tr').first().click()
    
    cy.get('h3').should('contain', 'Médias')
    cy.get('.media-gallery').should('be.visible')
  })

  it('Devrait afficher les rapports d\'une intervention', () => {
    cy.get('table tbody tr').first().click()
    
    cy.get('h3').should('contain', 'Rapports')
    cy.get('.reports-list').should('be.visible')
  })

  it('Devrait exporter les interventions', () => {
    cy.get('button').contains('Exporter').click()
    
    // Vérifier que le menu d'export s'affiche
    cy.get('.dropdown-menu').should('be.visible')
    cy.get('.dropdown-menu').should('contain', 'Excel')
    cy.get('.dropdown-menu').should('contain', 'CSV')
    cy.get('.dropdown-menu').should('contain', 'PDF')
  })

  it('Devrait trier les interventions par colonne', () => {
    // Trier par date
    cy.get('th').contains('Date').click()
    
    // Vérifier que l'ordre a changé
    cy.get('th').contains('Date').should('have.class', 'sort-asc')
    
    // Trier par statut
    cy.get('th').contains('Statut').click()
    
    // Vérifier que l'ordre a changé
    cy.get('th').contains('Statut').should('have.class', 'sort-asc')
  })
})
