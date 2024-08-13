# RAG using AWS Aurora, Langchain and Llama 3

### Goal

Point to the location of the datasource - codebase, pdf, etc. and ask questions about it.

### Index

1. [Sign-in Page](##Sign-in Page)
2. [Landing Page](##Landing Page)
3. [Chat Bot](##Open Form Button)

> Note - 
This project was built during a hackahton. Therefore, it is not production ready. 
You can use it for reference and build your own production ready solution.
> 

---

## Sign-in Page

![image.png](RAG%20using%20AWS%20Aurora,%20Langchain%20and%20Llama%203%202e96188ec2a84e08b44179aa23f2b843/image.png)

- Mandatory user sign-In for user tracking

---

## Landing Page

![image.png](RAG%20using%20AWS%20Aurora,%20Langchain%20and%20Llama%203%202e96188ec2a84e08b44179aa23f2b843/image%201.png)

- **Repository Details** - holds access to all information about your current data source and RAG status.
    - Repo Name and branch - tells the **name and branch of repository** that is being given as **context to the LLM**.
    - Actions -
        - Open Chat Bot - Link to open chat-bot.
        - Re-Sync - When data is changed at the source, a user can **re-sync** and **provide fresh context to LLM**.
        - Delete - **Delete** the **existing chat-bot** to free memory.

- **Open Form** Button  ****-
    - Use it to give location to the new datasource for chat-bot to train on.
    

![image.png](RAG%20using%20AWS%20Aurora,%20Langchain%20and%20Llama%203%202e96188ec2a84e08b44179aa23f2b843/image%202.png)

---

## Chat Bot

Directly chat with your datasource - 

[chat_only_demo.mp4](RAG%20using%20AWS%20Aurora,%20Langchain%20and%20Llama%203%202e96188ec2a84e08b44179aa23f2b843/chat_only_demo.mp4)

---
