# Mining-fee-remover
Remove mining fees from Claymore's miner - mine into your own wallet instead. This currently only works on Linux and EthOS.
Tested with version 9.8.

# How?

This program catches login packets sent to a ethereum stratum pool and modifies the target wallet address.

# TODO:

- Add config file
- Add support for custom worker names. This doesn't work now as modifying packet lenght forces pool to close connection.
- Windows version?

# Requirements

- Python3
- virtualenv

# Installation

Install requrements:

## Ubuntu

```
sudo apt-get install virtualenv python3 build-essential python-dev libnetfilter-queue-dev 
```

Clone this repository:
```
git clone https://github.com/tommarek/Mining-fee-remover.git
cd Mining-fee-remover
```

Create virtualenv, activate it and install necessary python modules:

```
virtualenv -p python3 venv
. venv/bin/activate
pip3 install -r requirements.txt
```

To deactivate virtualenv run

```
deactivate
```

### Autostart [optional]

If you want to run the script automatically after system boots up you need to edit files `systemd/mining_fee_remover.conf` and `service_start.sh`.
Make sure the paths on lines `7` and `3` respectively point to the correct directory where you've stored this git repo.
Then copy `upstart/mining-fee-remover.conf` to `/etc/init` directory.

```
sudo cp systemd/mining_fee_remover.conf /etc/systemd/system
```

After doing this you should run

```
sudo systemctl daemon-reload
sudo systemctl enable mining_fee_remover.service
sudo systemctl start mining_fee_remover.service
```

This should do the trick and next time you restart your rig the mining fee remover should start automatically.


## EthOS

```
sudo apt-get-ubuntu install python3 python3-pip
sudo pip3 install virtualenv
sudo apt-get-ubuntu install build-essential python-dev libnetfilter-queue-dev 
```

Clone this repository:
```
git clone https://github.com/tommarek/Mining-fee-remover.git
cd Mining-fee-remover
```

Create virtualenv, activate it and install necessary python modules:

```
virtualenv -p python3 venv
. venv/bin/activate
pip3 install -r requirements.txt
```

To deactivate virtualenv run

```
deactivate
```

### Autostart [optional]

If you want to run the script automatically after system boots up you need to edit files `upstart/mining-fee-remover.conf` and `service_start.sh`.
Make sure the paths on lines `13` and `3` respectively point to the correct directory where you've stored this git repo.
Then copy `upstart/mining-fee-remover.conf` to `/etc/init` directory.

```
sudo cp upstart/mining-fee-remover.conf /etc/init
```

After doing this you should run

```
sudo initctl reload-configuration
sudo initctl start mining-fee-remover
sudo initctl status mining-fee-remover
```

This should do the trick and next time you restart your rig the mining fee remover should start automatically.

# Configuration

This version of fee remover doesn't support config files so you will need to modify the source code.
You need to change:
- `pool` to the pool you are using (on line 88)
- `port` to the pool connection port (on line 89)
- `eth_wallet` address `0xda3e1e7822589a26e9705E184fC340e0731935eA` to yours (on line 90)
- `password` to your password (on line 91)
and save the modified file.

# Running the program

You need to turn off firewall to catch the packets:
```
sudo ufw disable
```

Start the virtualenv as root
```
cd Mining-fee-remover
sudo su
. venv/bin/activate
```

And run the program by executing (It needs to run as root because it's modifying iptables):
```
python mining_fee_remover.py
```

If you want the program to run in the background - so you can close the terminal window, run:

```
sudo python mining_fee_remover.py &
```

Now you can start your miner.
You must not run the miner with `-allcoins 1` nor  `-allpools 1` because the fee remover is listening on the port you've specified in Configuration and there is no way to guess which pool/port would the miner use to mine the fee.
Once the miner starts mining the dev fee it should mine to the wallet you've specified in the Configuration section.

To deactivate virtualenv run

```
deactivate
```

And to re-enable firewall run

```
sudo ufw enable
```

The logs (in case you want to check if the mining fee remover works correctly) can be found in `/var/log/mining-fee-remover.log`.

# Help
If you need any help then let me know and I'll try to help you.

# BTW
I don't encourage you to use this as Claymore deserves all the money he gets from the mining fees for making a great product.
I created this as it was a really interesting thing to do and it might help other people with simillar problems.

# Donations
If you found this useful please consider donating at least a small amount to:

ETH: `0xda3e1e7822589a26e9705E184fC340e0731935eA`

BTC: `3LE91QD9aCoCsM9vF8PXs755Vr7bmnoexQ`



