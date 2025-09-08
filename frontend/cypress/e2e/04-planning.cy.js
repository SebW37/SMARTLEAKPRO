// Tests E2E - Planning et calendrier - Phase Test & Debug
describe('Planning et calendrier', () => {
  beforeEach(() => {
    cy.login()
    cy.visit('/planning')
  })

  it('Devrait afficher le calendrier', () => {
    cy.get('h1').should('contain', 'Planning')
    cy.get('.calendar-container').should('be.visible')
    cy.get('.fc-calendar').should('be.visible')
  })

  it('Devrait afficher les vues du calendrier', () => {
    cy.get('.fc-button-group').should('be.visible')
    cy.get('.fc-button').should('contain', 'Jour')
    cy.get('.fc-button').should('contain', 'Semaine')
    cy.get('.fc-button').should('contain', 'Mois')
  })

  it('Devrait changer de vue du calendrier', () => {
    // Vue jour
    cy.get('.fc-button').contains('Jour').click()
    cy.get('.fc-daygrid-day').should('be.visible')
    
    // Vue semaine
    cy.get('.fc-button').contains('Semaine').click()
    cy.get('.fc-timegrid-week').should('be.visible')
    
    // Vue mois
    cy.get('.fc-button').contains('Mois').click()
    cy.get('.fc-daygrid-month').should('be.visible')
  })

  it('Devrait créer un nouveau rendez-vous', () => {
    // Cliquer sur une case du calendrier
    cy.get('.fc-daygrid-day').first().click()
    
    // Vérifier que le formulaire s'ouvre
    cy.get('.modal').should('be.visible')
    cy.get('.modal').should('contain', 'Nouveau rendez-vous')
    
    // Remplir le formulaire
    cy.get('select[name="client_id"]').select(1)
    cy.get('input[name="date_heure_debut"]').type('2024-12-31T10:00')
    cy.get('input[name="date_heure_fin"]').type('2024-12-31T12:00')
    cy.get('select[name="statut"]').select('planifie')
    cy.get('textarea[name="notes"]').type('Rendez-vous de test E2E')
    
    cy.get('button[type="submit"]').click()
    
    cy.get('.alert-success').should('contain', 'Rendez-vous créé avec succès')
  })

  it('Devrait modifier un rendez-vous existant', () => {
    // Supposer qu'il y a au moins un rendez-vous
    cy.get('.fc-event').first().click()
    
    // Vérifier que le formulaire s'ouvre
    cy.get('.modal').should('be.visible')
    cy.get('.modal').should('contain', 'Modifier le rendez-vous')
    
    // Modifier les détails
    cy.get('textarea[name="notes"]').clear().type('Notes modifiées E2E')
    
    cy.get('button[type="submit"]').click()
    
    cy.get('.alert-success').should('contain', 'Rendez-vous modifié avec succès')
  })

  it('Devrait supprimer un rendez-vous', () => {
    cy.get('.fc-event').first().click()
    
    cy.get('button').contains('Supprimer').click()
    
    // Confirmer la suppression
    cy.get('.modal').should('contain', 'Êtes-vous sûr de vouloir supprimer ce rendez-vous ?')
    cy.get('.modal button').contains('Confirmer').click()
    
    cy.get('.alert-success').should('contain', 'Rendez-vous supprimé avec succès')
  })

  it('Devrait déplacer un rendez-vous par drag & drop', () => {
    // Supposer qu'il y a au moins un rendez-vous
    cy.get('.fc-event').first().then(($event) => {
      const eventRect = $event[0].getBoundingClientRect()
      const targetRect = cy.get('.fc-daygrid-day').eq(3)[0].getBoundingClientRect()
      
      // Simuler le drag & drop
      cy.wrap($event)
        .trigger('mousedown', { which: 1 })
        .trigger('mousemove', { clientX: targetRect.left, clientY: targetRect.top })
        .trigger('mouseup')
    })
    
    // Vérifier que le rendez-vous a été déplacé
    cy.get('.alert-success').should('contain', 'Rendez-vous déplacé avec succès')
  })

  it('Devrait redimensionner un rendez-vous', () => {
    // Supposer qu'il y a au moins un rendez-vous
    cy.get('.fc-event').first().then(($event) => {
      const eventRect = $event[0].getBoundingClientRect()
      
      // Simuler le redimensionnement
      cy.wrap($event)
        .find('.fc-resizer')
        .trigger('mousedown', { which: 1 })
        .trigger('mousemove', { clientY: eventRect.bottom + 100 })
        .trigger('mouseup')
    })
    
    // Vérifier que le rendez-vous a été redimensionné
    cy.get('.alert-success').should('contain', 'Rendez-vous modifié avec succès')
  })

  it('Devrait afficher les statistiques du planning', () => {
    cy.get('.stats-cards').should('be.visible')
    cy.get('.stats-cards').should('contain', 'Rendez-vous aujourd\'hui')
    cy.get('.stats-cards').should('contain', 'Rendez-vous cette semaine')
    cy.get('.stats-cards').should('contain', 'Rendez-vous ce mois')
  })

  it('Devrait filtrer les rendez-vous par client', () => {
    cy.get('select[name="client_filter"]').select(1)
    cy.get('button').contains('Filtrer').click()
    
    // Vérifier que seuls les rendez-vous du client sélectionné s'affichent
    cy.get('.fc-event').should('have.length.at.least', 1)
  })

  it('Devrait filtrer les rendez-vous par statut', () => {
    cy.get('select[name="statut_filter"]').select('planifie')
    cy.get('button').contains('Filtrer').click()
    
    // Vérifier que seuls les rendez-vous planifiés s'affichent
    cy.get('.fc-event').should('have.length.at.least', 1)
  })

  it('Devrait naviguer dans le calendrier', () => {
    // Bouton précédent
    cy.get('.fc-prev-button').click()
    cy.get('.fc-toolbar-title').should('not.contain', 'Décembre 2024')
    
    // Bouton suivant
    cy.get('.fc-next-button').click()
    cy.get('.fc-toolbar-title').should('contain', 'Décembre 2024')
    
    // Bouton aujourd'hui
    cy.get('.fc-today-button').click()
    cy.get('.fc-today').should('have.class', 'fc-day-today')
  })

  it('Devrait afficher les conflits de planning', () => {
    // Créer un rendez-vous
    cy.get('.fc-daygrid-day').first().click()
    
    cy.get('select[name="client_id"]').select(1)
    cy.get('input[name="date_heure_debut"]').type('2024-12-31T10:00')
    cy.get('input[name="date_heure_fin"]').type('2024-12-31T12:00')
    cy.get('select[name="statut"]').select('planifie')
    cy.get('textarea[name="notes"]').type('Premier rendez-vous')
    
    cy.get('button[type="submit"]').click()
    
    // Essayer de créer un rendez-vous en conflit
    cy.get('.fc-daygrid-day').first().click()
    
    cy.get('select[name="client_id"]').select(1)
    cy.get('input[name="date_heure_debut"]').type('2024-12-31T11:00')
    cy.get('input[name="date_heure_fin"]').type('2024-12-31T13:00')
    cy.get('select[name="statut"]').select('planifie')
    cy.get('textarea[name="notes"]').type('Rendez-vous en conflit')
    
    cy.get('button[type="submit"]').click()
    
    // Vérifier l'alerte de conflit
    cy.get('.alert-warning').should('contain', 'Conflit de planning détecté')
  })

  it('Devrait exporter le planning', () => {
    cy.get('button').contains('Exporter').click()
    
    // Vérifier que le menu d'export s'affiche
    cy.get('.dropdown-menu').should('be.visible')
    cy.get('.dropdown-menu').should('contain', 'Excel')
    cy.get('.dropdown-menu').should('contain', 'CSV')
    cy.get('.dropdown-menu').should('contain', 'PDF')
  })

  it('Devrait imprimer le planning', () => {
    cy.get('button').contains('Imprimer').click()
    
    // Vérifier que la fenêtre d'impression s'ouvre
    cy.window().then((win) => {
      cy.stub(win, 'print').as('printStub')
    })
    
    cy.get('@printStub').should('have.been.called')
  })
})
