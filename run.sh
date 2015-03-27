echo "Starting docker container!"
echo "Current working directory: $(pwd)"

echo "Installing bower dependencies"
docker run -it --rm -v $(pwd):/srv/ dn_img bash -c 'bower --allow-root install'
echo "Starting server ..."
docker run -it --rm -p 80:8000 -v $(pwd):/srv/ dn_img
