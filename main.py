import random
import os
from github import Github
from dominate.tags import div, h1, p, h3, h4, a


class RPS:
    """Class for handling Rock Paper Scissors game via GitHub Issues."""

    def __init__(self, token, issue_number, repo):
        """Initialize the RPS game with GitHub authentication details."""
        self.token = token
        self.repo = Github(token).get_repo(repo)
        self.issue = self.repo.get_issue(issue_number)
        self.moves = ['rock', 'paper', 'scissor']
        self.file_path = 'README.md'

    def play_move(self):
        """Handles the user's move and updates the repository accordingly."""
        file_data = self.fetch_file_from_repo(self.file_path)
        user_name = self.issue.user.login
        move_data = self.issue.title.lower().split('|')

        if len(move_data) > 1 and move_data[1] in self.moves:
            move = move_data[1]
            self.computer_move = self.get_computer_move()

            if move in self.moves:
                result = self.did_user_win(move)
                new_file_data = self.gen_file_data(user_name, result)
                action = self.get_emoji(move)

                if result is True:
                    self.add_comment('Congratulations! You won! :tada:')
                    self.write_to_repo(
                        self.file_path,
                        f"@{user_name} won with {action}",
                        new_file_data,
                        file_data.sha
                    )
                elif result is None:
                    self.add_comment('Oops! This was a draw! :eyes:')
                    self.write_to_repo(
                        self.file_path,
                        f"@{user_name} played {action}",
                        new_file_data,
                        file_data.sha
                    )
                elif result is False:
                    action = self.get_emoji(self.computer_move)
                    self.add_comment(
                        f'Uh-Oh! You lost! :eyes:\n Computer played {self.computer_move}'
                    )
                    self.write_to_repo(
                        self.file_path,
                        f":robot: won with {action}",
                        new_file_data,
                        file_data.sha
                    )
        else:
            self.add_comment('You played an invalid move! :eyes:')

        self.issue.edit(state="closed")

    def get_emoji(self, move):
        """Returns the corresponding emoji for a given move."""
        if move == 'rock':
            return ":punch:"
        if move == 'paper':
            return ":hand:"
        return ":scissors:"

    def fetch_file_from_repo(self, filepath):
        """Fetches the specified file from the repository."""
        return self.repo.get_contents(filepath)

    def write_to_repo(self, filepath, message, content, sha):
        """Updates the specified file in the repository."""
        self.repo.update_file(filepath, message, content, sha)

    def add_comment(self, message):
        """Adds a comment to the GitHub issue."""
        self.issue.create_comment(message)

    def get_computer_move(self):
        """Generates a random move for the computer."""
        return random.choice(self.moves)

    def did_user_win(self, user_move):
        """Determines if the user won the round."""
        if (
            (user_move == 'rock' and self.computer_move == 'scissor') or
            (user_move == 'scissor' and self.computer_move == 'paper') or
            (user_move == 'paper' and self.computer_move == 'rock')
        ):
            return True
        if user_move == self.computer_move:
            return None
        return False

    def gen_file_data(self, user_name, result):
        """Generates the new README file content reflecting the game results."""
        outer = div()
        repo = self.repo.full_name

        with outer:
            h1("Rock Paper Scissors Game!")
            p("Click on one of the below actions to play your move:")
            h3(
                a(":punch:", href=f'https://github.com/{repo}/issues/new?title=rps|rock'),
                a(":hand:", href=f'https://github.com/{repo}/issues/new?title=rps|paper'),
                a(":scissors:", href=f'https://github.com/{repo}/issues/new?title=rps|scissor')
            )
            if result is True:
                h4(f"Previous winner was @{user_name} :tada:")
            elif result is False:
                h4("Previous winner was computer :robot:")
            else:
                h4("Previous game was a draw :eyes:")

        return outer.render()


if __name__ == '__main__':
    run = RPS(
        os.environ['TOKEN'],
        int(os.environ['ISSUE_NUMBER']),
        os.environ['REPO']
    )
    run.play_move()
