### Nice Translator TUI

A translator tui application based on python 3.x

![](./tran-tui.gif)

### Feature

- english-chinese dictionary
- languange translator. e.g You can translate Chinese to English or translate Japanese to Korean

### Installation

With pip in test.pypi.org:

``` bash
pip install -i https://test.pypi.org/simple/ nice-translator-tui
```

### Usage

After installation, type `tran` to open the tui app, and input any words/sentences and then press  `enter` key, you will get the result.

Before you use the translation part, you will need the `appId` and the `secretKey` which from https://fanyi-api.baidu.com/ and enable the [Genernal Translation API Service](https://fanyi-api.baidu.com/product/11).

The config file will be generated at you user home after the first time you launch the app(or you can place one by youself).

You can print the configuration file path with command `tranconfigpath`, note that  the file name should be `wox_nice_tran_config.json`

``` bash
youyinnn ~ ❯❯❯ tranconfigpath
C:\Users\youyinnn\wox_nice_tran_config.json
youyinnn ~ ❯❯❯
```

### Configuration

``` bash
{
    "app_id": "", # your app_id
    "secret_key": "", # your secret_key
    "target_languages": ["zh", "en", "jp", "kor"] # the language list you want to translate
}
```

