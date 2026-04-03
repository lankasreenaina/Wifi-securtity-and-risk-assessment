class SecurityAdvisor:
    def __init__(self):
        self.advice_map = {
            "Weak Encryption": {
                "recommendation": "Upgrade Wi-Fi encryption to WPA3-SAE or at least WPA2-AES (CCMP).",
                "action": "Change security settings in your router's wireless configuration page."
            },
            "No Encryption": {
                "recommendation": "Enable WPA3/WPA2 encryption immediately.",
                "action": "Set a strong password (minimum 12 characters) for your Wi-Fi network."
            },
            "Unknown Devices": {
                "recommendation": "Review connected devices and implement MAC filtering or change your Wi-Fi password.",
                "action": "Identify unrecognized devices in your router's 'Connected Devices' list. If suspicious, block them."
            },
            "High Device Density": {
                "recommendation": "Consider segmenting your network using VLANs or a separate Guest network.",
                "action": "Move IoT devices to a dedicated subnet to limit lateral movement risk."
            },
            "Too Many Open Ports": {
                "recommendation": "Disable unnecessary services and close unused ports on identified devices.",
                "action": "Audit devices like {details} and close ports via firewall or service management."
            },
            "Insecure Port Open": {
                "recommendation": "Immediately close insecure ports like FTP (21) or Telnet (23). Use secure alternatives like SFTP or SSH.",
                "action": "Disable legacy protocols on the device located at {details}."
            }
        }

    def generate_recommendations(self, vulnerabilities):
        recommendations = []
        seen_types = set()
        
        for vuln in vulnerabilities:
            vuln_type = vuln['Type']
            if vuln_type in self.advice_map and vuln_type not in seen_types:
                advice = self.advice_map[vuln_type]
                
                details = vuln.get('Details', '')
                rec_text = advice['recommendation'].format(details=details)
                action_text = advice['action'].format(details=details)
                
                recommendations.append({
                    "Vulnerability": vuln_type,
                    "Severity": vuln['Severity'],
                    "Recommendation": rec_text,
                    "Action": action_text
                })
                seen_types.add(vuln_type)
        
        # Default safety recommendation
        if not recommendations:
            recommendations.append({
                "Vulnerability": "General Security",
                "Severity": "LOW",
                "Recommendation": "Keep your router firmware updated and change passwords periodically.",
                "Action": "Check for firmware updates on your router manufacturer's website."
            })
            
        return recommendations

if __name__ == "__main__":
    advisor = SecurityAdvisor()
    sample_vulns = [{"Type": "Weak Encryption", "Severity": "CRITICAL"}]
    recs = advisor.generate_recommendations(sample_vulns)
    print(recs)
