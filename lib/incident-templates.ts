export interface IncidentTemplate {
  id: string
  name: string
  description: string
  severity: 'CRITICAL' | 'HIGH' | 'MEDIUM' | 'LOW'
  incident_type: string
  description_template: string
  checklist_items: string[]
}

export const incidentTemplates: IncidentTemplate[] = [
  {
    id: 'data-breach',
    name: 'Data Breach',
    description: 'Unauthorized access to sensitive data',
    severity: 'CRITICAL',
    incident_type: 'data_breach',
    description_template: `Data breach detected. Affected systems and data:
- Systems involved: [SPECIFY]
- Data types exposed: [e.g., PII, credentials, payment data]
- Estimated number of records: [NUMBER]
- Discovery date/time: [DATE/TIME]
- Initial impact assessment: [DESCRIBE]`,
    checklist_items: [
      'Isolate affected systems from network',
      'Collect forensic evidence',
      'Notify affected users',
      'Contact legal and compliance teams',
      'Prepare public statement',
      'Review access logs',
      'Implement containment measures',
      'Coordinate with law enforcement if necessary'
    ]
  },
  {
    id: 'malware',
    name: 'Malware Detection',
    description: 'Malicious software detected on systems',
    severity: 'HIGH',
    incident_type: 'malware',
    description_template: `Malware detected. Details:
- Malware type: [TYPE]
- Systems affected: [LIST]
- Detection method: [HOW DETECTED]
- Indicators of compromise: [IOCs]
- Lateral movement observed: [YES/NO]
- Data exfiltration: [YES/NO]`,
    checklist_items: [
      'Isolate infected systems',
      'Identify patient zero',
      'Scan all systems for indicators of compromise',
      'Review network traffic logs',
      'Check for data exfiltration',
      'Remove malware from systems',
      'Change credentials on affected systems',
      'Deploy endpoint protection updates',
      'Monitor for re-infection'
    ]
  },
  {
    id: 'ddos',
    name: 'DDoS Attack',
    description: 'Distributed denial of service attack',
    severity: 'HIGH',
    incident_type: 'ddos',
    description_template: `DDoS attack in progress. Attack details:
- Target service: [SERVICE]
- Attack volume: [GBPS/RPS]
- Attack type: [e.g., volumetric, protocol, application]
- Attack sources: [GEOGRAPHIC DISTRIBUTION]
- Service impact: [AFFECTED USERS/PERCENTAGE]
- Start time: [DATE/TIME]`,
    checklist_items: [
      'Activate DDoS mitigation',
      'Contact ISP/CDN provider',
      'Scale infrastructure if possible',
      'Implement rate limiting',
      'Redirect traffic to mitigation service',
      'Monitor mitigation effectiveness',
      'Preserve attack logs for analysis',
      'Communicate with affected users',
      'Prepare incident report'
    ]
  },
  {
    id: 'creds-leak',
    name: 'Credentials Leaked',
    description: 'User credentials exposed or compromised',
    severity: 'HIGH',
    incident_type: 'credentials_leak',
    description_template: `Credentials compromised. Details:
- Credential type: [e.g., API keys, passwords, tokens]
- Number of credentials: [NUMBER]
- Scope of compromise: [SYSTEMS/SERVICES AFFECTED]
- Source of leak: [HOW DISCOVERED]
- Exposure duration: [ESTIMATED TIME]
- Potential misuse: [YES/NO/CONFIRMED]`,
    checklist_items: [
      'Rotate all exposed credentials immediately',
      'Force password reset for affected users',
      'Revoke API keys and tokens',
      'Audit access logs for the credentials',
      'Check for unauthorized access',
      'Implement additional monitoring',
      'Enable MFA where applicable',
      'Notify affected users',
      'Review and strengthen credential management practices'
    ]
  },
  {
    id: 'unauthorized-access',
    name: 'Unauthorized Access',
    description: 'Suspicious or unauthorized user access',
    severity: 'MEDIUM',
    incident_type: 'unauthorized_access',
    description_template: `Unauthorized access detected. Details:
- Compromised account/system: [IDENTIFY]
- Access method: [LOGIN, VPN, SSH, etc.]
- Source IP address: [IP]
- Access time: [DATE/TIME]
- Data or systems accessed: [LIST]
- Suspicious activities: [DESCRIBE]`,
    checklist_items: [
      'Lock compromised account immediately',
      'Review account access logs',
      'Identify what data was accessed',
      'Trace source of access attempt',
      'Check for privilege escalation',
      'Audit other user accounts',
      'Reset credentials',
      'Review security group memberships',
      'Implement additional monitoring on account'
    ]
  },
  {
    id: 'config-change',
    name: 'Unauthorized Configuration Change',
    description: 'Unauthorized changes to system or application configuration',
    severity: 'MEDIUM',
    incident_type: 'config_change',
    description_template: `Configuration change detected. Details:
- System/service affected: [SPECIFY]
- Changes made: [DESCRIBE]
- Changed by: [USER/ACCOUNT]
- Change time: [DATE/TIME]
- Approval status: [APPROVED/UNAUTHORIZED]
- Impact: [DESCRIBE]`,
    checklist_items: [
      'Revert unauthorized changes',
      'Verify change was not approved',
      'Review change logs',
      'Check for system compromise',
      'Audit other recent changes',
      'Implement access controls',
      'Enable change notifications',
      'Review user permissions',
      'Document incident details'
    ]
  }
]
