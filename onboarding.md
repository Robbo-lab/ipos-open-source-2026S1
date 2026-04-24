# Onboarding

## Table of Contents

1. Introduction
2. Coding Standards
3. Documentation Standards
4. Test Coverage
5. Git Workflow
6. Issue Tracking
7. PR Merge Process
8. Development Environment Setup
9. Review Process
10. Communication Channels
11. Project Structure
12. Access and Permissions
13. Continuous Integration/Continuous Deployment
14. Release Process
15. Compliance and Security
16. Resources and Learning
17. Contacts
18. Feedback and Evaluation
19. FAQ
20. Appendices

---

## **1. Introduction**

Welcome to the **Task Management CLI Project**, a dynamic Python-based command-line application designed to create, manage, and filter tasks efficiently. Your role is to debug, enhance, and incorporate reusable components into this project while learning about open-source workflows and version control.

---

## **2. Coding Standards**

- Follow **PEP8** for code style and formatting.
- Ensure all added or modified code aligns with existing conventions.
- Use **meaningful variable names** and keep functions modular.

---

## **3. Documentation Standards**

- All public methods must include clear **docstrings** using the **Google Python Style Guide**.
- Update the `README.md` and inline comments for clarity when fixing or extending the application.

---

## **4. Test Coverage**

- Use the **`unittest` framework** for unit testing.
- Test coverage must increase for each PR.
- Ensure tests validate:
  - Task creation, deletion, and listing.
  - Date validation (using external components).
  - Duplicate prevention.

---

## **5. Git Workflow**

Follow **GitHub Flow**:

1. **Fork and Clone** the repository:

   ```bash
   git clone <repo-url>
   ```

2. **Create Issues** for bugs or enhancements.

3. **Branch Naming Convention**:
   - For bugs: `bugfix/<issue-number>`
   - For features: `feature/<feature-name>`

4. **Commit Messages**:  
   Use clear and descriptive messages. Example:

   ```bash
   git commit -m "Fix #123: Add date validation for task due dates"
   ```

5. **Push and Open PRs**:

   ```bash
   git push -u origin <branch-name>
   ```

---

## **6. Issue Tracking**

- Use GitHub Issues to document and track all bugs and features.
- Each Issue must include:
  - A clear title.
  - A description of the problem or feature.
  - Steps to reproduce (if applicable).
- Example:
  - Title: "Fix #1: Prevent duplicate tasks in task manager"

---

## **7. PR Merge Process**

1. Submit a **Pull Request (PR)** referencing the Issue number (`fixes #<issue_number>`).
2. Ensure all unit tests pass before submission.
3. Request a code review from the **lecturer/reviewer**.
4. Address feedback and resubmit as needed.

---

## **8. Development Environment Setup**

- **Python 3.9+** is required.
- Install dependencies:

  ```bash
  pip install -r requirements.txt
  ```

- Recommended tools:
  - IDE: PyCharm or Visual Studio Code.
  - Linter: `flake8` for PEP8 compliance.

---

## **9. Review Process**

- PR reviews focus on:
  - Code quality and readability.
  - Adherence to PEP8 and documentation standards.
  - Adequate unit test coverage.

---

## **10. Communication Channels**

- **Microsoft Teams** for announcements and technical discussions.
  - `#general` for updates.
  - `#pr-reviews` for sharing Pull Requests.

---

## **11. Project Structure**

```txt
task-manager-cli/
│
├── src/                       # Source code
│   ├── task.py                # Task class definition
│   ├── task_manager.py        # Core task management logic
│   ├── file_handler.py        # File handling with binary data
│
├── test/                      # Unit tests
│   ├── test_task_manager.py   # Tests for task manager functions
│   ├── test_file_handler.py   # Tests for file handling
│
├── main.py                    # Entry point for CLI app
├── requirements.txt           # Project dependencies
├── pyproject.toml             # Project setup for pip
└── README.md                  # Project documentation
```

---

## **12. Access and Permissions**

- Repository Access: Contact **Lecturer** if permissions are required.

---

## **13. Continuous Integration/Continuous Deployment**

- **GitHub Actions** automatically run:
  - Unit tests.
  - Linting for PEP8 compliance.
- Ensure your PR passes all checks.

---

## **14. Release Process**

- Submit PRs to the `main` branch.
- PR merges are reviewed by the lecturer/reviewer.
- Changes are tagged and versioned in accordance with the sprint cycle.

---

## **15. Compliance and Security**

- Enable **Two-Factor Authentication (2FA)** for GitHub.
- Do not share credentials or sensitive files.

---

## **16. Resources and Learning**

- [PEP8 Guidelines](https://www.python.org/dev/peps/pep-0008/)
- [Google Python Style Guide](https://github.com/google/styleguide/blob/gh-pages/pyguide.md)
- [Click Documentation](https://click.palletsprojects.com/)
- [Dateutil Documentation](https://dateutil.readthedocs.io/en/stable/)

---

## **17. Contacts**

- **Lecturer/Reviewer**: Jamie Robertson (<jamie.robertson@example.com>)
- **DevOps Admin**: Aarav Patel (<aarav.patel@example.com>)

---

## **18. Feedback and Evaluation**

- Provide feedback through GitHub Issues or during PR reviews.
- Your performance will be evaluated based on the assessment criteria.

---

## **19. FAQ**

- **Q: How do I run tests?**  
   A: Use the command `python -m unittest discover test`.

- **Q: How do I install dependencies?**  
   A: Run `pip install -r requirements.txt`.

---

## **20. Appendices**

- [GitHub Command Reference](https://docs.github.com/en/get-started)
- [Unit Testing with Python](https://docs.python.org/3/library/unittest.html)

---
