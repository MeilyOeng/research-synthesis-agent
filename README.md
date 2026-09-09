# research-synthesis-agent

Run tests with `pytest tests/test_faiss.py -s -v`.

For imports, the requirements file can be used to install everything with `pip install -r requirements.txt`.

install environment:

```bash
conda create -n research-agent python=3.11
conda activate research-agent
conda install -c conda-forge faiss-cpu
```