# buzzline-03-case

Streaming data does not have to be simple text.
Many of us are familiar with streaming video content and audio (e.g. music) files.

Streaming data can be structured (e.g. CSV files) or
semi-structured (e.g. JSON data).

We'll work with two different types of data, and we'll use two different Kafka topic names:
- JSON topic: `stock_alerts`
- CSV topic: `delivery_status`

See [.env](.env) for configuration.

## First, Use Tools from Module 1 and 2

Before starting, ensure you have completed the setup tasks in
<https://github.com/denisecase/buzzline-01-case> and
<https://github.com/denisecase/buzzline-02-case> first.  
**Python 3.11 is required.**

## Second, Copy This Example Project & Rename

1. Once the tools are installed, copy/fork this project into your GitHub account
   and create your own version of this project to run and experiment with.
2. Name it `buzzline-03-yourname` where `yourname` is something unique to you.

Additional information about our standard professional Python project workflow is available at
<https://github.com/denisecase/pro-analytics-01>.

Use your README.md to record your workflow and commands.

---

## Task 0. If Windows, Start WSL

- Be sure you have completed the installation of WSL as shown [here](https://github.com/denisecase/pro-analytics-01/blob/main/01-machine-setup/03c-windows-install-python-git-vscode.md).
- Open a **WSL terminal** from VS Code using:

```powershell
wsl
```

You should now be in a Linux shell.  
Do **all** steps related to starting Kafka in this WSL window.

---

## Task 1. Start Kafka (using WSL if Windows)

```bash
chmod +x scripts/prepare_kafka.sh
scripts/prepare_kafka.sh
cd ~/kafka
bin/kafka-server-start.sh config/kraft/server.properties
```

Keep this terminal open! Kafka is running and needs to stay active.

---

## Task 2. Manage Local Project Virtual Environment

### Windows

```powershell
py -3.11 -m venv .venv
.venv\Scripts\Activate.ps1
py -m pip install --upgrade pip wheel setuptools
py -m pip install --upgrade -r requirements.txt
```

### Mac / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
python3 -m pip install --upgrade pip
python3 -m pip install --upgrade -r requirements.txt
```

---

## Task 3. Start Kafka JSON Producer (`stock_alerts`)

This producer streams stock alert data as JSON messages.

**Windows:**

```shell
.venv\Scripts\activate
py -m producers.json_producer_stock_alerts
```

**Mac/Linux:**

```bash
source .venv/bin/activate
python3 -m producers.json_producer_stock_alerts
```

---

## Task 4. Start Kafka JSON Consumer (`stock_alerts`)

This consumer processes the JSON stock alert messages.

**Windows:**

```shell
.venv\Scripts\activate
py -m consumers.json_consumer_stock_alerts
```

**Mac/Linux:**

```bash
source .venv/bin/activate
python3 -m consumers.json_consumer_stock_alerts
```

---

## Task 5. Start Kafka CSV Producer (`delivery_status`)

This producer streams delivery status data as JSON messages from CSV.

**Windows:**

```shell
.venv\Scripts\activate
py -m producers.csv_producer_delivery_status
```

**Mac/Linux:**

```bash
source .venv/bin/activate
python3 -m producers.csv_producer_delivery_status
```

---

## Task 6. Start Kafka CSV Consumer (`delivery_status`)

This consumer processes delivery status messages.

**Windows:**

```shell
.venv\Scripts\activate
py -m consumers.csv_consumer_delivery_status
```

**Mac/Linux:**

```bash
source .venv/bin/activate
python3 -m consumers.csv_consumer_delivery_status
```

---

## How To Stop a Continuous Process

To kill the terminal, hit **CTRL + C**.

---

## Later Work Sessions

When resuming work on this project:

1. Open the project folder in VS Code.
2. Start the Kafka service (use WSL if Windows) and keep the terminal running.
3. Activate your virtual environment (.venv) in your OS-specific terminal.
4. Pull latest changes if needed:

```shell
git pull
```

---

## After Making Useful Changes

1. Add files to source control:

```shell
git add .
```

2. Commit changes:

```shell
git commit -m "Describe your changes here"
```

3. Push to GitHub:

```shell
git push -u origin main
```

---

## Save Space

You can delete `.venv` when not actively working and recreate it later.

---

## License

This project is licensed under the MIT License. See [LICENSE](LICENSE.txt).

