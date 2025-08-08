const express = require('express');
const cors = require('cors');
const app = express();
const PORT = 3001;

app.use(cors());
app.use(express.json());

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
  }
];

// Find suggested KEDBs
app.post('/api/suggested-kedbs', (req, res) => {
  const { description } = req.body;

  console.log('Finding KEDBs for:', description);

  // Simulate API delay
  setTimeout(() => {
    res.json({ kedbs: sampleKedbs });
  }, 1500);
});

// Generate KEDB content
app.post('/api/generate-kedb', (req, res) => {
  const { description } = req.body;

  console.log('Generating KEDB for:', description);

  // Simulate API delay
  setTimeout(() => {
    const content = `**KEDB Draft**

**Error:** ${description}

**Rootcause:** The job ${description} terminated unexpectedly. This specific cause requires further investigation but common causes include resource contention, downstream job failures, or issues within the job script itself.

**Resolution:**

**Description:** This KEDB entry provides steps to resolve the termination of the ${description} Autosys job in the PC3 environment. The steps involve checking job dependencies, examining logs, restarting the job, and escalating if necessary.

**Resolution Steps**

Step_Number: 1
Action: Check Job Dependencies
Command: job_depends | ${description} -d
Verification: Review the output for any failed dependencies.
Expected_Result: Output showing the dependencies of the job. If any dependent job failed, address that failure first.

Step_Number: 2
Action: Examine Autosys Logs
Command: Review job logs for errors
Verification: Check system logs and application logs for error messages
Expected_Result: Identify specific error that caused job termination`;

    res.json({ content });
  }, 2000);
});

app.listen(PORT, () => {
  console.log(`Sample KEDB API server running on http://localhost:${PORT}`);
  console.log('Available endpoints:');
  console.log('  POST /api/suggested-kedbs');
  console.log('  POST /api/generate-kedb');
});