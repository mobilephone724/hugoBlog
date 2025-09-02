---
title: github ssh 失败
slug: github-ssh-failed-2k9xdc
url: /post/github-ssh-failed-2k9xdc.html
date: '2025-02-03 08:44:15+08:00'
lastmod: '2025-03-02 19:57:33+08:00'
toc: true
isCJKLanguage: true
---



# github ssh 失败

## ssh 失败

* github 可能会屏蔽 22 的 ssh 端口，导致使用 ssh 协议拉取推送代码失败

* 解决方法为使用 443 端口，同时将 hostname 改为 `ssh.github.com`​

```rust
host github.com
  Hostname ssh.github.com
  User git
  IdentityFile ~/.ssh/github_mbp_linux
  Port 443
```

原因在 https://docs.github.com/en/authentication/troubleshooting-ssh/using-ssh-over-the-https-port 中有涉及。

‍

### 为什么使用 ProxyCommand 不可以：

```rust
Host github.com
  AddKeysToAgent yes
  UseKeychain yes
  IdentityFile ~/.ssh/id_ed25519
  ProxyCommand nc -x 127.0.0.1:7890 -X 5 %h %p
```

因为机场可能屏蔽 22 端口。
