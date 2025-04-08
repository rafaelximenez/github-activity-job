import requests
import os
from datetime import datetime, timedelta

def main():
    """Função principal para verificar a atividade do GitHub e enviar alertas no Slack.
    """

    github_username = os.environ.get('GITHUB_USERNAME')
    slack_webhook = os.environ.get('SLACK_WEBHOOK')
    github_token = os.environ.get('GITHUB_TOKEN')

    if not github_username or not slack_webhook or not github_token:
        print('Erro: Configure GITHUB_USERNAME, SLACK_WEBHOOK e GITHUB_TOKEN nas variáveis de ambiente.')
        return

    try:
        contributions = get_github_contributions(github_username, github_token)

        if not contributions:
            print(f'Erro: Não foi possível obter contribuições de {github_username}. Verifique as permissões do token ou o nome de usuário.')
            return

        contributions.sort(key=lambda x: datetime.strptime(x['date'], '%Y-%m-%dT%H:%M:%SZ'), reverse=True)

        last_contribution = contributions[0]
        last_contribution_date_str = datetime.strptime(last_contribution['date'], '%Y-%m-%dT%H:%M:%SZ').strftime('%Y-%m-%d')
        last_contribution_date = datetime.strptime(last_contribution['date'], '%Y-%m-%dT%H:%M:%SZ')
        days_since_last_contribution = (datetime.now().date() - last_contribution_date.date()).days

        if days_since_last_contribution > 2:
            message = f"⚠️ *Atenção!*\n\n*Última contribuição foi em*: {last_contribution_date_str} há {days_since_last_contribution} dias.\n\n*Repositório*: {last_contribution['repo_name']}\n\n*Msg commit*: {last_contribution['message']}."
            send_slack_message(slack_webhook, message)
            print(f'Mensagem enviada para o Slack. {days_since_last_contribution} dias')

        else:
            print(f"Última contribuição de {github_username} foi há {days_since_last_contribution} dias. Sem alerta necessário.")

    except Exception as e:
        print(f'Erro: {e}')


def get_github_contributions(username, github_token):
    """Obtém as atividades relevantes do GitHub de um usuário (PushEvents e PullRequestEvents)."""

    url = f"https://api.github.com/users/{username}/events"
    headers = {"Authorization": f"Bearer {github_token}", "Accept": "application/vnd.github+json"}

    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        events = response.json()

        activity_data = []
        for event in events:
            repo_name = event['repo']['name'] if 'repo' in event and 'name' in event['repo'] else 'N/A'
            message = event['payload']['commits'][0]['message'] if 'payload' in event and 'commits' in event['payload'] and event['payload']['commits'] else 'N/A'
            activity_data.append({
                "date": event['created_at'],
                "repo_name": repo_name,
                "message": message,
                "type": "Push"
            })
        return activity_data

    except requests.exceptions.RequestException as e:
        print(f"Erro ao obter eventos do GitHub: {e}")
        return []


def send_slack_message(webhook_url, message):
    """Envia uma mensagem para o Slack via webhook.
    """
    payload = {"text": message}
    try:
        response = requests.post(webhook_url, json=payload)
        response.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(f"Erro ao enviar mensagem para Slack: {e}")


if __name__ == "__main__":
    main()