# Daily Operations.

## Original

This article is copied from [Github で fork したリポジトリの簡便な同期と運用](https://qiita.com/jsasaki/items/f77c23f4fea3f7edb812) on Qiita.

Thanks to the author, [Jun Sasaki](https://qiita.com/jsasaki).

---

オープンソース（本家）の Github リポジトリ（**upstream**）を fork し，**upstream** のアップデートを 自身の Github リポジトリ （**origin**）に手動で取得することで簡便に同期し，運用する方法の備忘録です．**upstream** の対象ブランチは **master** （永続ブランチ）とします．なお，本家へのプルリクエストは想定せず（してもよいですが），**origin** の **master** は **upstream** の純粋なコピーを維持します．

## upstreamの永続ブランチ master と originの永続ブランチ master および main を用意

実際の開発は **master** から分岐した **main** を永続ブランチとして Github-flow で管理し，**main** から分岐した **feature** ブランチ（名前は適宜変更）で開発・修正を行い，Github の プルリクエスト で **main** に マージ します．本家の **master** がアップデートされたら適当なタイミングで上記を実行します．

## 本家のリポジトリを fork しローカルに git clone

本家のリポジトリを自身の Github に fork し，それをローカルに git clone し，ローカルリポジトリのディレクトリに移動します．このとき `git branch` で確認し，**master** が現在のブランチであることを想定します．

```bash
git clone git@github.com:<user>/<repo>.git
```

## 本家のリポジトリを upstream として登録
**upstream** として指定する **URL** は `git@github.com:<user>/<repo>.git` のような Clone するときの SSHのURLです．

```bash
git remote add upstream URL
git remote -v  # 確認
```

## upstream を ローカルリポジトリに取得
`fetch` コマンドで **upstream** をローカルリポジトリに取得します．ローカルの作業ディレクトリ（ワークツリー）への反映は行われません（作業ディレクトリの変更なし）．
`fetch` の引数については[こちら](https://qiita.com/matsumon-development/items/b37b1ce988fb810eb8ac)が参考になります．

```bash
git fetch upstream
```

これで `upstream/master` が new branch として追加されます．`git branch -a` で確認すると以下のようになっているでしょう．

```bash
* master
  remotes/origin/HEAD -> origin/master
  remotes/origin/master
  remotes/upstream/master
```

## main ブランチを作成し，デフォルトブランチに設定

origin での永続ブランチとして，main ブランチを作成します．

```bash
git checkout -b main
git push origin main
```

この状態では origin （Github）のデフォルトブランチは master のままですので，main に変更します．
Github の当該リポジトリにおいて，メニュー右端の Settings をクリックして現れる左側のメニューから Branches をクリックします．Default branch に現れる master の右端にある両方向矢印 ⇄ をクリックするとボックスが現れます．その master プルダウンから main を選択し，update をクリックします．最後に確認が現れますので，それをクリックします．
この状態で `git branch -a` で確認すると，以下のように `remotes/origin/HEAD` は `origin/master` を指したままであることが分かります．

```bash
* main
  master
  remotes/origin/HEAD -> origin/master
  remotes/origin/main
  remotes/origin/master
  remotes/upstream/master
```

そこで，以下を実行します．

```bash
git remote set-head origin main
```

すると，以下の通り `origin/main` を指すように変更されます．

```bash
* main
  master
  remotes/origin/HEAD -> origin/main
  remotes/origin/main
  remotes/origin/master
  remotes/upstream/master
```

以上で，最初の準備が完了です．

## 日々の作業前の確認

featureブランチで作業中の場合，以下のようにmasterブランチへの切り替えができません．

```bash
$ git checkout master
error: Your local changes to the following files would be overwritten by checkout:
        ...
Please commit your changes or stash them before you switch branches.
Aborting
```

featureでコミットしておくか，またはスタッシュに隠しておく必要があります．まだ作業中であればスタッシュが標準選択でしょう．

```bash
git stash
```

後でfeatureに戻って来たら元に戻します．

```bash
git checkout feature
git stash pop
```

## upstream を ローカル に マージ し，origin に プッシュ

現在のブランチを **master** にして，取得した **upstream/master** を ローカルの **master** に マージ します．次に，ローカルの **master** を **origin/master** に プッシュ します．

```bash
git checkout master
git merge upstream/master
git push origin master
```

これで本家（**upstream/master**）と ローカルの **master** および **origin/master** の同期が完了です．

今後，同期を継続するには，本家がアップデートされる度に，同じように `git fetch upstream` でローカルリポジトリに **upstream/master** を取得し，`merge` と `push` の一連の作業を実行します．

## さらに tag を同期

このままでは tag が同期されませんので，tag が存在する場合は以下を実行します．

```bash
git pull upstream master --tags
git push origin master --tags
```

## master を main に マージ

更新された **master** を **main** にマージし，プッシュします．main ブランチが存在しない**初回**は master ブランチにおいて，`git checkout -b main` により，master から 分岐した main ブランチを作成します．

```bash
git checkout main
git merge master
git push origin main
```

コンフリクトが発生する場合は，後述の通り対応します．また，**初回** は `git remote set-head origin main` を実行し，リモートリポジトリ origin のデフォルトブランチ を main にしておきます．Github でもデフォルトブランチを main に変更する手続きが必要のようです．

## 更新された main ブランチを feature ブランチに マージ

**feature** ブランチで作業中に（コミットまたはスタッシュしておきます） **upstream/master** の更新を取得して **main** ブランチが更新された場合を想定し，その **main** ブランチを **feature** ブランチに マージ します．この作業が必要なのは main から feature へ分岐後に main が更新された場合です．main の更新がない場合は次の **プルリクエスト で main へ マージ** に飛びます．

```bash
git checkout feature
git merge main
```

ターミナルに `CONFLICT (content): Merge conflict in coawst.bash` のように **CONFLICT** で始まる行が現れたら，その行で示されたファイル中にコンフリクト（競合）の内容が書き込まれています．そのファイルをエディタで開き，適切に編集します．
以下のコンフリクト内容の例では `<<<<<<< HEAD` から `=======` までが feature の，`=======` から `>>>>>>> main` までが main の内容となっており，両者に競合があることが分かります．

```bash
<<<<<<< HEAD
#export   NETCDF_CONFIG=/usr/bin/nc-config
=======
export   NETCDF_CONFIG=/usr/bin/nf-config
#export   NETCDF_CONFIG=/vortexfs1/apps/impistack-1.0/bin/nf-config
>>>>>>> main
```

これを例えば以下のように不要な行を削除する等，適切に編集します．この例では main を残しました．

```bash
export   NETCDF_CONFIG=/usr/bin/nf-config
#export   NETCDF_CONFIG=/vortexfs1/apps/impistack-1.0/bin/nf-config
```

また，以下のようなCONFLICTにおいて，削除すると決めた場合は `git rm` で，残す場合は `git add` で対処します．以下は消去の場合です．

```bash
CONFLICT (modify/delete): mydir/myfile deleted in main and modified in HEAD. Version HEAD of mydir/myfile left in tree.

git rm mydir/myfile
```

編集が完了したら 更新ファイルを `add` した後，コミット します．コミット時のコメントをファイル毎に変える必要がなければ，すべてのファイルへの対応完了後にまとめてコミットしても構いません．自動マージ可能なファイル（自身では編集しなかったファイル）もコミットする必要があります．

```bash
git add file_name  # ファイル毎に
git add -u         # 更新されたファイルをまとめて
git commit -m "comment"
```

## プルリクエスト（プルリク） で feature を main にマージ

**feature** での作業が完了し，**main** に マージ するときは変更理由等をわかりやすく履歴として残すため Github の プリリクエスト を用いることとします．まず，Github (origin) に feature を プッシュ します．

```bash
git push origin feature
```

このプッシュ直後に Github に移ると，**Compare & pull request** のボタンが一番上に現れていると思います．これをクリックします．現れていない場合は pull request を探して，クリックください．
左側にマージする先，右側に今プッシュしたブランチが現れ，左向きの矢印 ← で繋がれています．左側が目的のマージ先になっているか確認して適切に設定します．おそらくデフォルトは upstream の master リポジトリになっていると思いますので，それが意図したものでなければ修正します．ここでは origin main にしました．
その下のタイトルとコメントを入力し，**Create pull request** をクリックします．
コンフリクトがなければ下に現れる **Merge pull request** をクリックし，続けて **Confirm merge** をクリックします．
上記の流れで行う限り，コンフリクトはローカルで main を feature にマージしたところで解消されているはずですので，この プルリクエスト ではコンフリクトは起こらないはずです．この記事での プルリクエスト の目的はあくまで改変の記録をわかりやすく管理するためです．

## ローカルリポジトリの更新

origin/main が更新されましたので，これをローカルリポジトリに反映させます．この過程ではコンフリクトは発生せず，`Fast-forward merge` となります．

```bash
git checkout main
git pull origin main
```

featureブランチは一旦削除しましょう．必要があれば改めてfeatureブランチを作成しましょう．

```bash
git branch -d feature
```

## スパコン専用ブランチの運用

スパコンのローカルリポジトリには永続ブランチの main とスパコン専用ブランチ sc を持たせ，main を sc にマージするものとします（sc を main にマージする場合は上記の通り，Githubのプルリクで対応するものとします）．main をチェックアウトし，Github (origin) の main から更新を取り込み，sc にマージします．

```bash
git checkout main
git pull origin main
git checkout sc
git merge main
```

これまでと同様にコンフリクトに対応し，Github (origin) にプッシュします．

```bash
git push origin sc
```

さらに origin/main に取り込む場合は Github のプルリクで対応します．

## デフォルトブランチの変更
Githubでデフォルトブランチを変更するには左上のブランチのボタンをクリックし，下端の **View all branches** をクリックし，デフォルトブランチバー右端の **⇄** ボタンをクリックし，次の画面でも **⇄** ボタンをクリックして設定を進めます．

例えば，Githubのデフォルトブランチを master から main に変更し，ローカルブランチも同様に変更したつもりでも以下のように変わらないことがありました．

```bash
remotes/origin/HEAD -> origin/master
```

これを `remotes/origin/HEAD -> origin/main`に変更するには main ブランチにおいて，以下のようにします．

```bash
git remote set-head origin main
```

## feature のプッシュを取り消したい場合

[こちら](https://qiita.com/S42100254h/items/db435c98c2fc9d4a68c2)と[こちら](https://awesome-linus.com/2019/03/09/git-push-by-mistake/)を参考に， feature において `git reset --soft HEAD^`でローカルの変更を残しながらコミットを取り消し，`git push origin +feature` で origin の feature ブランチへ強制的にプッシュします．なお `+feature` はfeatureブランチ名の先頭に `+` を付けており，これが強制を意味します．


# Github に SSH接続
ディレクトリ `~/.ssh/` に移動し，秘密鍵と公開鍵を作成します．`-t`: 暗号化方式を指定，`-b`: 暗号化強度を指定，`-C`: コメントを設定 です．

```bash
$ ssh-keygen -t rsa -b 4096 -C "username@hoge.com"
Enter file in which to save the key (/home/account/.ssh/id_rsa):
Enter passphrase (empty for no passphrase):
Enter same passphrase again:
```

秘密鍵のファイル名を求められますが，デフォルトとするため，何も入力せずに Enter を押します．続いて **passphrase** を２回入力します．

Github にログインし，右上ボタンのプルダウンで **Settings** → **SSH and GPG keys** に移動します．右上の **New SSH key** ボタンをクリックし，**Title** （ロカールマシン名等，適当な名前）と作成した公開鍵を **Key** に貼り付け，**Add SSH key** をクリックします．

### 秘密鍵を ssh-agent に登録する
passphrase を聞かれますので，入力します．

```bash
$ ssh-add ~/.ssh/id_rsa
```
もしエラーが出たら，以下のように対応します．passphraseの入力が必要です．
```bash
Could not open a connection to your authentication agent.
$ eval "$(ssh-agent)"
Agent pid *******
$ ssh-add ~/.ssh/id_rsa
Enter passphrase for id_rsa:
```

以下を実行して，**passphrase** を入力し，`Hi your_account! You've successfully authenticated, but GitHub does not provide shell access.` のようなメッセージが現れれば成功です．

```bash
ssh -T git@github.com
```

もし以下のようになった場合は `yes`と回答します．

```
The authenticity of host 'github.com (**.**.***.***)' can't be established.
ECDSA key fingerprint is ***************************************************.
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
Warning: Permanently added 'github.com,**.**.***.***' (ECDSA) to the list of known hosts.
Hi *****! You've successfully authenticated, but GitHub does not provide shell access.
```

### リモートURLがHTTPSの場合の注意

SSH接続に変更しましょう．すでに，他のリポジトリがSSHで接続できている場合は，`.git/config`を開き，`url = `の行だけ以下のように書き換えるだけです．

```Git
[core]
	repositoryformatversion = 0
	filemode = false
	bare = false
	logallrefupdates = true
	ignorecase = true
[remote "origin"]
	url = git@github.com:***/***.git
	fetch = +refs/heads/*:refs/remotes/origin/*
[branch "main"]
	remote = origin
	merge = refs/heads/main
```

**以下は古い情報です**
2021年8月13日以降，HTTPSの場合はパスワードではなく，[アクセストークンでの認証](https://qiita.com/shiro01/items/e886aa1e4beb404f9038) が必要になっています．アクセストークンをコピーし，`Password for 'https://***@github.com':` にペーストします．何も表示されませんが，そのままEnterを入力します．アクセストークンは1ヶ月有効ですが，それが表示されたページから移動すると再表示できません．Githubにログインした状態で [**こちら**](https://github.com/settings/tokens) で再作成表示できます．

### 参考資料
- [GitHubにSSH接続しようとして引っかかった話](https://zenn.dev/keikuchen/articles/cffa31d69ecaae7e91d7)
- [GitHubにssh接続できるようにする（Qiita）](https://qiita.com/0ta2/items/25c27d447378b13a1ac3)
- [GithubのSSH通信設定](https://qiita.com/yysskk/items/974c9c55d66a26515651)
- [一人プルリクエストのすゝめ](https://crieit.net/posts/9c710ef2383a3703649ee712a9eb86e6)
- [GitHubがパスワード認証を廃止するらしいので](https://qiita.com/shiro01/items/e886aa1e4beb404f9038)
