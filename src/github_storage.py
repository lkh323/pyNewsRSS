import json
import os
from github import Github, GithubException
import streamlit as st

class GitHubStorage:
    def __init__(self, token, repo_name):
        self.github = Github(token)
        self.repo = self.github.get_repo(repo_name)

    def load_json(self, path):
        """Loads a JSON file from the repository."""
        try:
            content_file = self.repo.get_contents(path)
            json_content = content_file.decoded_content.decode('utf-8')
            return json.loads(json_content)
        except GithubException as e:
            if e.status == 404:
                return None  # File not found
            else:
                st.error(f"Error loading {path}: {e}")
                return None
        except Exception as e:
            st.error(f"An unexpected error occurred loading {path}: {e}")
            return None

    def save_json(self, path, data, commit_message):
        """Saves a JSON file to the repository. Creates or updates."""
        try:
            json_content = json.dumps(data, indent=2, ensure_ascii=False)
            
            # Check if file exists to decide between create or update
            try:
                content_file = self.repo.get_contents(path)
                # If exists, update
                self.repo.update_file(
                    path=path,
                    message=commit_message,
                    content=json_content,
                    sha=content_file.sha
                )
            except GithubException as e:
                if e.status == 404:
                    # If not exists, create
                    self.repo.create_file(
                        path=path,
                        message=commit_message,
                        content=json_content
                    )
                else:
                    raise e
            return True
        except Exception as e:
            st.error(f"Error saving {path}: {e}")
            return False

    def list_files(self, path):
         """List files in a directory"""
         try:
             contents = self.repo.get_contents(path)
             return [content.path for content in contents]
         except GithubException as e:
             if e.status == 404:
                 return []
             raise e
