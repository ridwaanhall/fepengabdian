# README

This is the README file for the backend of the Pengabdian project.

# Run the backend locally

<!-- .env -->

Create .env file in the root directory of the backend with the following content:

```env
SECRET_KEY=your_secret_key
ALGORITHM=HS256
``` 

To run the backend in Docker, you need to have Docker installed on your machine. If you don't have Docker installed, you can download it from [here](https://www.docker.com/products/docker-desktop).

After you have Docker installed, you can run the following command to build the Docker image:

```bash
docker build -t pengabdian-backend .
```

After the image is built, you can run the following command to run the Docker container:

```bash
docker run -d -p 8000:80 pengabdian-backend
```

The backend will be running on port 8000. You can access the backend by going to [http://localhost](http://localhost) in your browser.