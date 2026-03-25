# ToDo-App-Docker

A simple, containerized ToDo application built with Flask and SQLAlchemy, using SQLite as the database. The application is fully dockerized and orchestrated using Docker Compose for easy deployment and development.

## Description

This project demonstrates a basic ToDo list web application where users can add, view, edit, complete, and delete tasks. The app consists of a Flask backend serving a web interface and a separate SQLite database container. Data persistence is achieved through a shared Docker volume.

## Features

- **Add Tasks**: Create new ToDo items with a simple form.
- **View Tasks**: Display all tasks, separated into pending and completed sections.
- **Edit Tasks**: Inline editing of task titles.
- **Complete Tasks**: Mark tasks as completed or uncompleted with checkboxes.
- **Delete Tasks**: Remove tasks permanently.
- **Persistent Storage**: Tasks are stored in an SQLite database with data persistence via Docker volumes.
- **RESTful API**: Optional JSON API endpoints for programmatic access.
- **Responsive UI**: Clean, simple web interface with CSS styling.

## Prerequisites

Before running this application, ensure you have the following installed on your system:

- [Docker](https://docs.docker.com/get-docker/)
- [Docker Compose](https://docs.docker.com/compose/install/)

## Installation

1. **Clone the repository**:
   ```bash
   git clone https://github.com/jakegithub24/ToDo-App-Docker.git
   cd ToDo-App-Docker
   ```

2. **Build and start the containers**:
   ```bash
   docker-compose up --build
   ```

   This command will:
   - Build the Flask app container from `flask-app/Dockerfile`.
   - Build the SQLite database container from `sqlite-container/Dockerfile`.
   - Start both services with the shared volume for data persistence.

3. **Access the application**:
   Open your web browser and navigate to `http://localhost:5000`.

## Usage

### Web Interface

- **Adding a Task**: Enter a task title in the input field and click "Add".
- **Completing a Task**: Check the checkbox next to a task to mark it as completed.
- **Editing a Task**: Click the "Edit" button next to a task, modify the text, and press Enter or click away to save.
- **Deleting a Task**: Click the "Delete" button next to a task to remove it.

### API Endpoints

The application also provides RESTful API endpoints for programmatic access:

- **GET /todos**: Retrieve all tasks as JSON.
- **POST /todos**: Add a new task. Send JSON data with `title` and optional `completed` fields.

Example API usage with curl:

```bash
# Get all tasks
curl http://localhost:5000/todos

# Add a new task
curl -X POST http://localhost:5000/todos \
  -H "Content-Type: application/json" \
  -d '{"title": "New Task", "completed": false}'
```

## Project Structure

```
ToDo-App-Docker/
├── docker-compose.yml          # Docker Compose configuration
├── flask-app/                  # Flask application
│   ├── app.py                  # Main Flask application
│   ├── Dockerfile              # Dockerfile for Flask app
│   ├── requirements.txt        # Python dependencies
│   ├── static/
│   │   └── style.css           # CSS styles for the web interface
│   └── templates/
│       └── index.html          # HTML template for the web interface
├── sqlite-container/           # SQLite database container
│   ├── Dockerfile              # Dockerfile for SQLite setup
│   └── init-db.sh              # Database initialization script
├── LICENSE                     # GPL-3.0 License
└── README.md                   # This file
```

## Development

To run the application in development mode:

1. Start the containers:
   ```bash
   docker-compose up --build
   ```

2. The Flask app will run with `FLASK_ENV=development`, enabling debug mode.

3. For code changes, rebuild the containers as needed.

## Stopping the Application

To stop the running containers:

```bash
docker-compose down
```

To also remove the volumes (which will delete all data):

```bash
docker-compose down -v
```

## Contributing

Contributions are welcome! Please follow these steps:

1. Fork the repository.
2. Create a new branch for your feature or bug fix.
3. Make your changes and test them thoroughly.
4. Submit a pull request with a clear description of your changes.

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

---

Made with ❤️ by [jakegithub24](https:/github.com/jakegithub24/)