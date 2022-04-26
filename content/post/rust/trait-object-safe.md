---
title: "Trait Object Safe"
date: 2022-04-26T12:36:56+08:00
draft: true
---

```sh
$ cargo c
#...
error[E0038]: the trait `source::Binary` cannot be made into an object
  --> src/manager.rs:36:22
   |
36 |     fn bin(&self) -> &Box<dyn Binary>;
   |                      ^^^^^^^^^^^^^^^^ `source::Binary` cannot be made into an object
   |
note: for a trait to be "object safe" it needs to allow building a vtable to allow the call to be resolvable dynamically; for more information visit <https://doc.rust-lang.org/reference/items/traits.html#object-safety>
  --> src/source.rs:23:29
   |
23 | pub trait Binary: Visible + Clone + Send + Sync {
   |           ------            ^^^^^ ...because it requires `Self: Sized`
   |           |
   |           this trait cannot be made into an object...

For more information about this error, try `rustc --explain E0038`.
warning: `binaries` (lib) generated 10 warnings
```

<!--more-->

```rust
#[async_trait]
pub trait Visible {
    async fn latest_ver(&self) -> Result<String>;

    async fn get_url(&self, ver: &str) -> Result<Url>;

    // async fn get_latest_url(&self) -> Result<Url> {
    //     self.get_url(&self.latest_ver().await?).await
    // }
}

pub trait Binary: Visible + Clone + Send + Sync {
    fn name(&self) -> &str;

    fn version(&self) -> Version;

    fn exe_glob(&self) -> Option<&str>;

    fn hook(&self) -> Option<&Hook>;
}

#[async_trait]
pub trait Package1: Send + Sync {
    fn bin(&self) -> &Box<dyn Binary>;

    async fn has_installed(&self) -> bool {
        let name = self.bin().name().to_owned();
        tokio::task::spawn_blocking(move || {
            which(&name).map_or(false, |p| {
                trace!("found executable bin {} in {}", name, p.display());
                true
            })
        })
        .await
        .unwrap_or_else(|e| {
            error!("failed spawn blocking `which` task: {}", e);
            false
        })
    }

    async fn updateable_ver(&self) -> Option<(String, String)>;

    async fn install(&self, ver: &str) -> Result<()>;

    async fn install_latest(&self) -> Result<()> {
        self.install(&self.bin().latest_ver().await?).await
    }

    async fn uninstall(&self) -> Result<()>;

    async fn update(&self) -> Result<()> {
        if let Some((new, old)) = self.updateable_ver().await {
            info!("updating version to {} from {}", new, old);
            self.uninstall().await?;
            self.install(&new).await?;
            Ok(())
        } else {
            bail!("can not update")
        }
    }
}
```

TODO

参考：

* [The Rust Reference: Object Safety](https://doc.rust-lang.org/reference/items/traits.html#object-safety)
* [Error E0038](https://doc.rust-lang.org/error-index.html#E0038)
