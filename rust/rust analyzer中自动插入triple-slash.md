# rust analyzer中自动插入triple-slash `///`

rust analyzer不能自动在`///`开始键入enter后连续插入`///`如：

```rust
/// 按下enter时下一行不能以`///`开头

fn a() {}
```

## 解决方案

VS Code: Add the following to keybindings.json:

```json
// Place your key bindings in this file to override the defaultsauto[]
[
    {
        "key": "Enter",
        "command": "rust-analyzer.onEnter",
        "when": "editorTextFocus && !suggestWidgetVisible && editorLangId == rust"
    }
]
```

参考：

- [On Enter](https://rust-analyzer.github.io/manual.html#on-enter)
