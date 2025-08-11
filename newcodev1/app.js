import React, { useState, useEffect } from 'react';
import { saveAs } from 'file-saver';
import { Document, Packer, Paragraph, TextRun } from 'docx';
import FeaturesPage from './components/FeaturesPage';
import Tooltip from './components/Tooltip';
import './App.css';

const App = () => {
  const [incidentDescription, setIncidentDescription] = useState('CTR PC3 CTR.WEEKLY_UNDETECT_REPORT_CLEANUP_V2.B - JOBTERMINATED');
  const [currentView, setCurrentView] = useState('input');
  const [editorContent, setEditorContent] = useState('');
  const [selectedKedb, setSelectedKedb] = useState(null);
  const [suggestedKedbs, setSuggestedKedbs] = useState([]);
  const [loading, setLoading] = useState(false);
  const [showFeatures, setShowFeatures] = useState(false);

  const appVersion = '1.2.0';

  // Sample KEDB data
  const sampleKedbs = [
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
  ];

  // Simulate API call for finding KEDBs
  const handleFindKedb = async () => {
    if (!incidentDescription.trim()) {
      alert('Please enter an incident description');
      return;
    }

    setLoading(true);
    try {
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 1500));
      setSuggestedKedbs(sampleKedbs);
      setCurrentView('suggested');
    } catch (error) {
      console.error('Error fetching KEDBs:', error);
      alert('Failed to fetch KEDBs');
    } finally {
      setLoading(false);
    }
  };

  // Simulate API call for generating KEDB
  const handleGenerateKedb = async () => {
    if (!incidentDescription.trim()) {
      alert('Please enter an incident description');
      return;
    }

    setLoading(true);
    try {
      // Simulate API delay
      await new Promise(resolve => setTimeout(resolve, 2000));
      
      const generatedContent = `**KEDB Draft**

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
Expected_Result: Identify specific error that caused job termination

Step_Number: 3
Action: Restart the Job
Command: sendevent -E FORCE_STARTJOB -J ${incidentDescription}
Verification: Check if job starts successfully
Expected_Result: Job should start and run without errors`;

      setEditorContent(generatedContent);
      setCurrentView('editor');
    } catch (error) {
      console.error('Error generating KEDB:', error);
      alert('Failed to generate KEDB');
    } finally {
      setLoading(false);
    }
  };

  // Handle opening a KEDB
  const handleOpenKedb = (kedb) => {
    setSelectedKedb(kedb);
    setEditorContent(kedb.content);
    setCurrentView('editor');
  };

  // Handle cancel - return to suggested view
  const handleCancel = () => {
    setCurrentView('suggested');
    setEditorContent('');
    setSelectedKedb(null);
  };

  // Handle version click - show features page
  const handleVersionClick = () => {
    setShowFeatures(true);
  };

  // Close features page
  const closeFeaturesPage = () => {
    setShowFeatures(false);
  };

  // Download content as DOCX
  const handleDownload = async () => {
    if (!editorContent.trim()) return;

    try {
      // Convert markdown-like content to plain text
      const plainText = editorContent
        .replace(/\*\*(.*?)\*\*/g, '$1')
        .replace(/\*(.*?)\*/g, '$1')
        .split('\n')
        .filter(line => line.trim())
        .join('\n\n');

      const doc = new Document({
        sections: [{
          properties: {},
          children: [
            new Paragraph({
              children: [
                new TextRun({
                  text: "KEDB Document",
                  bold: true,
                  size: 28
                })
              ]
            }),
            new Paragraph({ text: "" }),
            ...plainText.split('\n').map(line => 
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

      const buffer = await Packer.toBuffer(doc);
      const blob = new Blob([buffer], { 
        type: 'application/vnd.openxmlformats-officedocument.wordprocessingml.document' 
      });
      saveAs(blob, `KEDB_Document_${Date.now()}.docx`);
    } catch (error) {
      console.error('Error creating DOCX:', error);
      // Fallback to text download
      const blob = new Blob([editorContent], { type: 'text/plain' });
      saveAs(blob, `KEDB_Document_${Date.now()}.txt`);
    }
  };

  // Auto-load KEDBs on mount
  useEffect(() => {
    setSuggestedKedbs(sampleKedbs);
  }, []);

  // Show features page if requested
  if (showFeatures) {
    return <FeaturesPage onClose={closeFeaturesPage} version={appVersion} />;
  }

  return (
    <div className="kedb-app">
      {/* Header */}
      <header className="header">
        <h1>KEDB Draft Generator App</h1>
        <div className="header-right">
          <div className="version-info">
            <span className="version-text">Current Version: </span>
            <button 
              className="version-link"
              onClick={handleVersionClick}
              title="Click to view live features"
            >
              v{appVersion}
            </button>
          </div>
          <Tooltip 
            content="This KEDB Draft Generator helps you find existing KEDB entries and generate new ones for incident resolution. Enter an incident description, find relevant KEDBs, or generate new documentation."
          >
            <div className="info-icon">ℹ</div>
          </Tooltip>
        </div>
      </header>

      {/* Input Section - Always Visible */}
      <section className="input-section">
        <label>Enter Incident Short Description</label>
        <input
          type="text"
          value={incidentDescription}
          onChange={(e) => setIncidentDescription(e.target.value)}
          className="form-control"
          disabled={loading}
        />
        
        <div className="button-group">
          <button 
            className="btn btn-secondary" 
            onClick={handleFindKedb}
            disabled={loading}
          >
            {loading ? 'Finding...' : 'Find KEDB'}
          </button>
          <button 
            className="btn btn-primary" 
            onClick={handleGenerateKedb}
            disabled={loading}
          >
            {loading ? 'Generating...' : 'Generate KEDB'}
          </button>
        </div>
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

export default App;
