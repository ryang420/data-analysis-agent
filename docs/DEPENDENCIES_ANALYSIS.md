# requirements.txt 依赖分析

## 1. 是否有间接依赖？

**有。** 当前 `requirements.txt` 共 **135 行**，相当于一次 `pip freeze` 的完整输出，里面既有**直接依赖**，也有大量**间接依赖**（被直接依赖拉进来的子依赖）。

### 典型间接依赖示例

| 包名 | 被谁依赖 | 说明 |
|------|----------|------|
| botocore | boto3 | AWS SDK 核心 |
| starlette | fastapi | ASGI 框架 |
| httpx, httpcore, h11 | langchain / requests | HTTP 客户端 |
| jinja2, Mako | alembic | 模板 |
| certifi, urllib3, charset-normalizer, idna | requests | HTTP 底层 |
| pydantic_core, annotated-types | pydantic | 校验与类型 |
| numpy | pandas | 数值计算 |
| contourpy, cycler, fonttools, kiwisolver, pillow | matplotlib | 绘图 |
| greenlet | SQLAlchemy | 异步 |
| sniffio, anyio | httpx | 异步 I/O |
| markdown-it-py, Pygments | rich | 终端输出 |
| ... | ... | 其余多为传递依赖 |

这些都不需要（也不建议）在「顶层」需求里逐一手写，交给 pip 解析即可。

---

## 2. 依赖是否可以瘦身？

**可以。** 建议只维护**直接依赖**，让 pip 自动解决间接依赖。

### 2.1 项目实际用到的直接依赖（按代码扫描）

根据对 `src/` 和 `scripts/` 的 import 分析，**直接使用**的第三方包如下：

| 类别 | 包 | 使用位置 |
|------|----|----------|
| Web | fastapi, uvicorn | main.py |
| LLM/Agent | langchain, langchain_openai, langgraph, openai | agents/, main.py, node_log.py |
| 图/检查点 | langgraph-checkpoint-postgres, psycopg, psycopg_pool | memory_saver.py |
| 数据库 | SQLAlchemy, psycopg2-binary | database/, import_csv_to_db.py |
| 存储 | boto3 | s3_storage.py |
| 校验/类型 | pydantic | 多处 |
| HTTP/文件 | requests, chardet | file.py |
| 环境 | python-dotenv | db.py |
| 数据/表格 | pandas, openpyxl | file.py, import_csv_to_db.py |
| 文档 | python-pptx, pypdf, docx2python | file.py |
| 迁移 | alembic | 若做 DB 迁移则保留 |

### 2.2 当前 requirements 中未在代码里 import 的包

以下在**当前代码**中未直接出现，可视为「未使用」或「仅间接/可选」：

- **Authlib, beautifulsoup4** — 未使用
- **GitPython, gitignore_parser** — 未使用
- **matplotlib, seaborn** — 未使用
- **opencv-python** — 未使用
- **xlrd, xlsxwriter** — 未使用（Excel 只用到 pandas + openpyxl）
- **sqlacodegen** — 仅开发/代码生成
- **watchdog** — 未使用
- **dbus-python, PyGObject** — 系统/GUI，非服务端必需
- **APScheduler** — 仅在日志 filter 名称中出现，若未跑定时任务可移除
- **setuptools, wheel** — 构建用，可不进应用 requirements

上述可从「应用运行」的 requirements 中移除或挪到 `requirements-dev.txt`。

### 2.3 瘦身做法建议

1. **使用 `requirements.in` 只列直接依赖**  
   已生成 `requirements.in`，只包含上面确认过的直接依赖（及可选开发依赖注释）。

2. **用 pip-tools 生成锁表**  
   ```bash
   pip install pip-tools
   pip-compile requirements.in -o requirements.txt
   ```  
   得到的 `requirements.txt` 会包含所有传递依赖并带版本号，便于复现环境。

3. **开发依赖单独文件（可选）**  
   将 pytest、pylint、isort、coverage 等放进 `requirements-dev.txt`，生产环境只装主 requirements。

4. **验证**  
   在新 venv 中执行：  
   `pip install -r requirements.txt`  
   然后跑测试和主要入口，确认无缺包。

---

## 3. 小结

| 问题 | 结论 |
|------|------|
| 是否有间接依赖？ | 有，当前 135 行里多数为间接依赖。 |
| 依赖能否瘦身？ | 能，只维护直接依赖（如 `requirements.in`），用 pip-tools 生成完整 `requirements.txt`。 |

按上述方式瘦身后，**维护的是少量直接依赖**，**间接依赖由工具自动计算并锁定**，既干净又可复现。
