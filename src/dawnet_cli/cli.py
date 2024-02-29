import click
from questionary import prompt

from .api import get_remotes

# # Function to fetch or generate a joke
# def get_joke():
#     return "Why don't scientists trust atoms? Because they make up everything!"
#
# # Main CLI command
# @click.command()
# @click.option('--name', prompt='Your name', help='The name of the person to greet.')
# @click.option('--tell-joke', is_flag=True, help='Tell a joke after greeting.')
# def main(name, tell_joke):
#     """Simple CLI that greets the user and optionally tells them a joke."""
#     greeting = f"Hello, {name}!"
#     click.echo(greeting)
#
#     if tell_joke:
#         # Use Questionary to ask if the user really wants to hear a joke
#         questions = [
#             {
#                 'type': 'confirm',
#                 'name': 'wants_joke',
#                 'message': 'Do you really want to hear a joke?',
#                 'default': True,
#             },
#         ]
#         answers = prompt(questions)
#
#         if answers.get('wants_joke', False):
#             joke = get_joke()
#             click.echo(joke)
#         else:
#             click.echo("No joke for you today!")

@click.command()
def list():
    remote_list = get_remotes()
    for remote in remote_list:
        print(remote)

@click.command()
def main():
    list()


if __name__ == '__main__':
    main()
