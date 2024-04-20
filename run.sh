docker build -t cats/subvortex .

docker stop subvortex-miner
docker rm subvortex-miner
docker run -it -p 9999:9999 --name subvortex-miner cats/subvortex python3 neurons/miner.py --netuid 7 --subtensor.network finney --wallet.name fsealcold --wallet.hotkey fsealhot --logging.debug --axon.port 9999