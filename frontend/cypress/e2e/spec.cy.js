describe('Recruiter Dashboard', () => {

  it('opens dashboard', () => {
    cy.visit('http://localhost:3000')

    cy.contains('Overview').should('be.visible')
  })

  it('opens Candidates page', () => {
    cy.visit('http://localhost:3000')

    cy.contains('Candidates').click()

    cy.contains('Candidate profiles').should('be.visible')
  })

  it('opens Sessions page', () => {
    cy.visit('http://localhost:3000')

    cy.contains('Sessions').click()

    cy.contains('Sessions').should('be.visible')
  })

})

describe('Data Export', () => {
  const mockSessions = {
    sessions: [
      {
        session_id: 'session-1',
        candidate_id: 'candidate-1',
        status: 'completed',
        start_time: '2024-01-15T10:00:00',
        risk_score: 0.2
      },
      {
        session_id: 'session-2',
        candidate_id: 'candidate-2',
        status: 'completed',
        start_time: '2024-01-16T14:00:00',
        risk_score: 0.5
      }
    ]
  }

  const mockPdfBlob = new Blob(['%PDF-1.4 fake pdf content'], { type: 'application/pdf' })

  beforeEach(() => {
    // Stub the download mechanism
    cy.window().then((win) => {
      cy.stub(win.URL, 'createObjectURL').returns('blob:fake-url')
      cy.stub(win.URL, 'revokeObjectURL').as('revokeURL')
    })
  })

  describe('Sessions Page CSV Export', () => {
    it('exports CSV when clicking Export CSV button', () => {
      // Intercept API calls
      cy.intercept('GET', '**/active-sessions*', { sessions: [] }).as('activeSessions')
      cy.intercept('GET', '**/completed-sessions*limit=10000*', mockSessions).as('completedSessions')
      cy.intercept('GET', '**/failed-sessions*limit=10000*', { sessions: [] }).as('failedSessions')

      cy.visit('http://localhost:3000/sessions')
      
      // Wait for data to load
      cy.wait('@activeSessions')
      cy.wait('@completedSessions')
      cy.wait('@failedSessions')

      // Click Export CSV button
      cy.contains('button', 'Export CSV').click()

      // Verify createObjectURL was called (download triggered)
      cy.window().then((win) => {
        expect(win.URL.createObjectURL).to.have.been.called
      })

      // Verify success toast
      cy.contains('CSV exported successfully').should('be.visible')
    })

    it('shows error when no data available', () => {
      cy.intercept('GET', '**/active-sessions*', { sessions: [] }).as('activeSessions')
      cy.intercept('GET', '**/completed-sessions*', { sessions: [] }).as('completedSessions')
      cy.intercept('GET', '**/failed-sessions*', { sessions: [] }).as('failedSessions')

      cy.visit('http://localhost:3000/sessions')
      
      cy.wait('@activeSessions')
      cy.wait('@completedSessions')
      cy.wait('@failedSessions')

      cy.contains('button', 'Export CSV').click()

      cy.contains('No data to export').should('be.visible')
    })
  })

  describe('Candidates Page CSV Export', () => {
    it('exports CSV when clicking Export CSV button', () => {
      cy.intercept('GET', '**/completed-sessions*limit=10000*', mockSessions).as('completedSessions')
      cy.intercept('GET', '**/failed-sessions*limit=10000*', { sessions: [] }).as('failedSessions')

      cy.visit('http://localhost:3000/candidates')
      
      cy.wait('@completedSessions')
      cy.wait('@failedSessions')

      cy.contains('button', 'Export CSV').click()

      cy.window().then((win) => {
        expect(win.URL.createObjectURL).to.have.been.called
      })

      cy.contains('CSV exported successfully').should('be.visible')
    })
  })

  describe('Analytics Page CSV Export', () => {
    it('exports CSV when clicking Export button', () => {
      cy.intercept('GET', '**/completed-sessions*limit=10000*', mockSessions).as('completedSessions')
      cy.intercept('GET', '**/failed-sessions*limit=10000*', { sessions: [] }).as('failedSessions')

      cy.visit('http://localhost:3000/analytics')
      
      cy.wait('@completedSessions')
      cy.wait('@failedSessions')

      cy.contains('button', 'Export').click()

      cy.window().then((win) => {
        expect(win.URL.createObjectURL).to.have.been.called
      })
    })
  })

  describe('Session Detail PDF Export', () => {
    const mockSessionDetail = {
      session_id: 'session-1',
      candidate_id: 'candidate-1',
      status: 'completed',
      start_time: '2024-01-15T10:00:00',
      video_analysis: {
        facial_expressions: JSON.stringify({ happy: 0.8, neutral: 0.2 }),
        gaze_direction: 'forward',
        confidence_score: 0.85
      },
      audio_analysis: {
        sentiment: 'positive',
        clarity_score: 0.9,
        speaking_pace: 'normal',
        filler_word_count: 2
      },
      ai_feedback: {
        overall_feedback: 'Excellent performance'
      }
    }

    it('exports PDF successfully using backend', () => {
      cy.intercept('GET', '**/active-sessions*', mockSessions).as('activeSessions')
      cy.intercept('GET', '**/session-status/session-1', mockSessionDetail).as('sessionStatus')
      cy.intercept('GET', '**/sessions/session-1/report/pdf', {
        statusCode: 200,
        headers: { 'content-type': 'application/pdf' },
        body: mockPdfBlob
      }).as('pdfDownload')

      cy.visit('http://localhost:3000/sessions')
      cy.wait('@activeSessions')

      // Click on first session to open detail modal
      cy.contains('session-1').click()
      cy.wait('@sessionStatus')

      // Click Export PDF button
      cy.get('[aria-label="Export PDF"]').click()

      cy.wait('@pdfDownload')

      // Verify success toast for complex report
      cy.contains('Complex report generated').should('be.visible')
    })

    it('falls back to browser PDF when backend fails', () => {
      cy.intercept('GET', '**/active-sessions*', mockSessions).as('activeSessions')
      cy.intercept('GET', '**/session-status/session-1', mockSessionDetail).as('sessionStatus')
      cy.intercept('GET', '**/sessions/session-1/report/pdf', {
        statusCode: 500,
        body: { detail: 'PDF generation failed' }
      }).as('pdfDownloadFail')

      cy.visit('http://localhost:3000/sessions')
      cy.wait('@activeSessions')

      cy.contains('session-1').click()
      cy.wait('@sessionStatus')

      cy.get('[aria-label="Export PDF"]').click()

      cy.wait('@pdfDownloadFail')

      // Verify fallback toast for basic report
      cy.contains('Basic report generated').should('be.visible')
    })

    it('shows error when both backend and browser PDF fail', () => {
      cy.intercept('GET', '**/active-sessions*', mockSessions).as('activeSessions')
      cy.intercept('GET', '**/session-status/session-1', mockSessionDetail).as('sessionStatus')
      cy.intercept('GET', '**/sessions/session-1/report/pdf', {
        statusCode: 500,
        body: { detail: 'PDF generation failed' }
      }).as('pdfDownloadFail')

      // Mock jsPDF to throw error
      cy.visit('http://localhost:3000/sessions')
      cy.window().then((win) => {
        win.jsPDF = class {
          constructor() {
            throw new Error('jsPDF initialization failed')
          }
        }
      })

      cy.wait('@activeSessions')

      cy.contains('session-1').click()
      cy.wait('@sessionStatus')

      cy.get('[aria-label="Export PDF"]').click()

      cy.wait('@pdfDownloadFail')

      // Verify error toast
      cy.contains('Failed to export PDF').should('be.visible')
    })

    it('disables button while PDF is being generated', () => {
      cy.intercept('GET', '**/active-sessions*', mockSessions).as('activeSessions')
      cy.intercept('GET', '**/session-status/session-1', mockSessionDetail).as('sessionStatus')
      cy.intercept('GET', '**/sessions/session-1/report/pdf', {
        statusCode: 200,
        headers: { 'content-type': 'application/pdf' },
        body: mockPdfBlob,
        delay: 1000 // Delay to test loading state
      }).as('pdfDownload')

      cy.visit('http://localhost:3000/sessions')
      cy.wait('@activeSessions')

      cy.contains('session-1').click()
      cy.wait('@sessionStatus')

      cy.get('[aria-label="Export PDF"]').click()

      // Button should be disabled during export
      cy.get('[aria-label="Export PDF"]').should('be.disabled')

      cy.wait('@pdfDownload')

      // Button should be enabled after export
      cy.get('[aria-label="Export PDF"]').should('not.be.disabled')
    })
  })
})