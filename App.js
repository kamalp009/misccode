import React, { useState, useRef } from 'react';
import * as XLSX from 'xlsx';
import { saveAs } from 'file-saver';
import { Document, Packer, Paragraph, TextRun } from 'docx';
import { fetchSuggestedKedbs, generateKedbContent } from './services/apiService';
import Tooltip from './components/Tooltip';
import './App.css';

const KEDBApp = () => {
  const [incidentDescription, setIncidentDescription] = useState('CTR PC3 CTR.WEEKLY_UNDETECT_REPORT_CLEANUP_V2.B - JOBTERMINATED');
  const [currentView, setCurrentView] = useState('input'); // input, suggested, editor
  const [editorContent, setEditorContent] = useState('');
  const [selectedKedb, setSelectedKedb] = useState(null);
  const [suggestedKedbs, setSuggestedKedbs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');
  const fileInputRef = useRef(null);

  // Handle Find KEDB - API call
  const handleFindKedb = async () => {
    if (!incidentDescription.trim()) {
      setError('Please enter an incident description');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const data = await fetchSuggestedKedbs(incidentDescription);
      setSuggestedKedbs(data);
      setCurrentView('suggested');
    } catch (err) {
      console.error('Error fetching KEDBs:', err);
      setError('Failed to fetch KEDBs. Using fallback data.');

      // Fallback data
      setSuggestedKedbs([
        {
          id: 'KB0092892',
          title: 'Generic_KEDB_CRCD_MAXRUN App_ID: CRCD Issue: MAXRUNALARM/JOBFAILURE/JOBTERMINATED: CRCD_%_B Symptom/Intake: Netcool Incident Alert / Notification on MAXRUNALARM/JOBFAILURE/JOBTERMINATED in',
          recommended: true,
          content: `**KEDB View**

**How to solve the failure:**

1. Login & navigation information: Login to Autosys Workload Automation (crvrt6000b.wwt1farm.com) through UID and file password.

2. On the left side, click Views, select CRCD-PROD, and expand

3. Please check the job status on right side of windows in Autosys by giving below details:

Select Jobs and Alerts
Give Name of the failed job
Click Go. You will get latest job status as you can see below:
4. Check if the job is still running. The Maxrun alarm is raised for CRCD because of the Latency issue.

5. Please monitor the job for 2-3 hours after the alert was received. (This is expected behavior due to nature of the job because of data center latency).`
        },
        {
          id: 'KB0082635',
          title: 'C2T - Cleanup DQE job C2TZ2_156**%_DQE*%_CL_C failure due to recovery file lock issue or run time issue',
          recommended: false,
          content: `**KEDB View**

**How to solve the failure:**

1. Check the DQE job status in the system
2. Verify if there are any file lock issues
3. Review the job logs for specific error messages
4. Restart the cleanup process if necessary
5. Monitor the job completion`
        },
        {
          id: 'KB0090234',
          title: 'Generic_CEODS_BOX_JOB_MAXRUNALARM App_ID: CEODS Issue:',
          recommended: false,
          content: `**KEDB View**

**How to solve the failure:**

1. Navigate to CEODS job monitoring interface
2. Check the MAXRUNALARM status
3. Review job dependencies and prerequisites
4. Verify system resources availability
5. Execute job restart procedure if needed`
        }
      ]);
      setCurrentView('suggested');
    } finally {
      setLoading(false);
    }
  };

  // Handle Generate KEDB - API call
  const handleGenerateKedb = async () => {
    if (!incidentDescription.trim()) {
      setError('Please enter an incident description');
      return;
    }

    setLoading(true);
    setError('');

    try {
      const generatedContent = await generateKedbContent(incidentDescription);
      setEditorContent(generatedContent);
      setCurrentView('editor');
    } catch (err) {
      console.error('Error generating KEDB:', err);
      setError('Failed to generate KEDB. Using fallback content.');

      // Fallback generated content
      const fallbackContent = `**KEDB Draft**

**Error:** ${incidentDescription}

**Rootcause:** The job ${incidentDescription} terminated unexpectedly. This specific cause requires further investigation but common causes include resource contention, downstream job failures, or issues within the job script itself.

**Resolution:**

**Description:** This KEDB entry provides steps to resolve the termination of the ${incidentDescription} Autosys job in the PC3 environment. The steps involve checking job dependencies, examining logs, restarting the job, and escalating if necessary.

**Resolution Steps**

Step_Number: 1
Action: Check Job Dependencies
Command: job_depends | ${incidentDescription} -d
Verification: Review the output for any failed dependencies.
Expected_Result: Output showing the dependencies of the job. If any dependent job failed, address that failure first.

Step_Number: 2
Action: Examine Autosys Logs
Command: Review job logs for errors
Verification: Check system logs and application logs for error messages
Expected_Result: Identify specific error that caused job termination`;

      setEditorContent(fallbackContent);
      setCurrentView('editor');
    } finally {
      setLoading(false);
    }
  };

  // Handle Open KEDB
  const handleOpenKedb = (kedb) => {
    setSelectedKedb(kedb);
    setEditorContent(kedb.content);
    setCurrentView('editor');
  };

  // Handle Cancel
  const handleCancel = () => {
    setCurrentView('suggested');
    setEditorContent('');
    setSelectedKedb(null);
    setError('');
  };

  // Handle Download as DOCX
  const handleDownload = async () => {
    if (!editorContent.trim()) return;

    try {
      // Create DOCX document
      const doc = new Document({
        sections: [{
          properties: {},
          children: [
            new Paragraph({
              children: [
                new TextRun({
                  text: "KEDB Document",
                  bold: true,
                  size: 32
                })
              ]
            }),
            new Paragraph({
              children: [
                new TextRun({
                  text: "",
                  break: 2
                })
              ]
            }),
            ...editorContent.split('\n').map(line => 
              new Paragraph({
                children: [
                  new TextRun({
                    text: line,
                    size: 24
                  })
                ]
              })
            )
          ]
        }]
      });

      // Generate and download
      const buffer = await Packer.toBuffer(doc);
      const blob = new Blob([buffer], { 
        type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' 
      });
      saveAs(blob, 'KEDB_Document.docx');
    } catch (error) {
      console.error('Error creating DOCX:', error);
      // Fallback to text download
      const blob = new Blob([editorContent], { type: 'text/plain' });
      saveAs(blob, 'KEDB_Document.txt');
    }
  };

  return (
    <div className="kedb-app">
      {/* Header - Always Visible */}
      <header className="header">
        <h1>KEDB Draft Generator App</h1>
        <Tooltip 
          content="This KEDB Draft Generator helps you find existing KEDB entries and generate new ones for incident resolution. Enter an incident description, find relevant KEDBs, or generate new documentation."
        >
          <div className="info-icon">
            ℹ
          </div>
        </Tooltip>
      </header>

      {/* Input Section - Always Visible */}
      <section className="input-section">
        <div className="form-group">
          <label>Enter Incident Short Description</label>
          <input
            type="text"
            value={incidentDescription}
            onChange={(e) => setIncidentDescription(e.target.value)}
            className="form-control"
            disabled={loading}
          />
        </div>
        <div className="button-group">
          <button 
            className="btn btn-secondary" 
            onClick={handleFindKedb}
            disabled={loading}
          >
            {loading && currentView === 'input' ? 'Finding...' : 'Find KEDB'}
          </button>
          <button 
            className="btn btn-primary" 
            onClick={handleGenerateKedb}
            disabled={loading}
          >
            {loading && currentView === 'input' ? 'Generating...' : 'Generate KEDB'}
          </button>
        </div>
        {error && <div className="error-message">{error}</div>}
      </section>

      {/* Loading Indicator */}
      {loading && (
        <div className="loading-section">
          <div className="loading-spinner"></div>
          <p>Processing your request...</p>
        </div>
      )}

      {/* Suggested KEDBs Section */}
      {currentView === 'suggested' && !loading && (
        <section className="suggested-section">
          <h2>Suggested KEDB's</h2>
          <div className="kedb-list">
            {suggestedKedbs.map((kedb, index) => (
              <div key={kedb.id} className="kedb-item">
                <div className="kedb-header">
                  <span className="kedb-number">{index + 1}.</span>
                  <span className="kedb-id">{kedb.id}:</span>
                  <span className="kedb-title">{kedb.title}</span>
                  {kedb.recommended && (
                    <span className="recommended-badge">(Recommended)</span>
                  )}
                </div>
                <button 
                  className="btn btn-open"
                  onClick={() => handleOpenKedb(kedb)}
                >
                  Open
                </button>
              </div>
            ))}
          </div>
        </section>
      )}

      {/* Editor Section */}
      {currentView === 'editor' && !loading && (
        <section className="editor-section">
          <div className="editor-header">
            <h3>Document content</h3>
          </div>
          <textarea
            className="editor-textarea"
            value={editorContent}
            onChange={(e) => setEditorContent(e.target.value)}
            rows={20}
            placeholder="KEDB content will appear here..."
          />
          <div className="editor-actions">
            <button className="btn btn-secondary" onClick={handleCancel}>
              Cancel
            </button>
            <button 
              className="btn btn-success" 
              onClick={handleDownload}
              disabled={!editorContent.trim()}
            >
              Download
            </button>
          </div>
        </section>
      )}
    </div>
  );
};

export default KEDBApp;