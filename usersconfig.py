import json

class UserKeys:
    def __init__(self):
        self.users_config = [
            {
                "user_name": "Jean Dupont",
                "user_key": "UUID-USER-1",
                "it_domain": "Cloud Infrastructure",
                "skills": ["Kubernetes", "Docker", "GCP", "Terraform"],
                "personalized_system_prompt": ("You are a cloud infrastructure expert specializing in Kubernetes and cloud-native technologies. Respond in French with technical precision."
                                                "You will assist your user Jean Dupont by Providing detailed, technical, and concise answers.")
            },
            {
                "user_name": "Marie Leclerc",
                "user_key": "UUID-USER-2",
                "it_domain": "DevOps & CI/CD",
                "skills": ["Jenkins", "GitLab CI", "Ansible", "Python Automation"],
                "personalized_system_prompt": "You are a DevOps specialist focusing on CI/CD pipelines and automation. You will assist your user Marie Leclerc, by Providing detailed, technical, and concise answers. Provide detailed, practical advice in French."
            },
            {
                "user_name": "Pierre Martin",
                "user_key": "UUID-USER-3",
                "it_domain": "Cybersecurity",
                "skills": ["Network Security", "Penetration Testing", "Firewall Configuration"],
                "personalized_system_prompt": "You are a cybersecurity expert who can provide in-depth security analysis and recommendations. Respond in French with a focus on practical security measures."
            },
            {
                "user_name": "Sophie Dubois",
                "user_key": "UUID-USER-4",
                "it_domain": "Data Engineering",
                "skills": ["Apache Spark", "Big Data", "Python", "Data Pipelines"],
                "personalized_system_prompt": "You are a data engineering specialist who can discuss complex data processing and analytics solutions. Respond in French with technical depth."
            },
            {
                "user_name": "Lucas Fontaine",
                "user_key": "UUID-USER-5",
                "it_domain": "Cloud Native Development",
                "skills": ["Microservices", "Golang", "Kubernetes", "Istio"],
                "personalized_system_prompt": "You are a cloud-native development expert specializing in microservices architecture. Provide comprehensive, technical responses in French."
            }
        ]

    def get_user_by_key(self, user_key):
        for user in self.users_config:
            if user['user_key'] == user_key:
                return user
        return None

    def to_json(self):
        return json.dumps(self.users_config, indent=2)
