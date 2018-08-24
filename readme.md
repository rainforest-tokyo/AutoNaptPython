# AutoNaptPython

<details><summary>広いレンジのPORTで待ち受けをして、受信したデータでプロトコル判定を
行い、後ろにいるハニーポットなどにデータを流すツール。</summary></details>

<image src="./images/ports.png" width=70%>

## 起動方法例: 
	./autonapt.sh 

## 使い方
	python autonapt.py [--ports <port-setting.json>] [--protocols <protocol-setting.json>] [--bind <bind-ip-address>] [--log <logfile>] [--elastic]
	  --ports     : lisenするポートの設定を記述したファイルを指定 規定値は ./ports.json
	  --protocols : プロトコルの判定と接続先の設定を記述したファイルを指定 規定値は ./protocol.json
	  --bind      : bindをするアドレスを指定 規定値はINADDR_ANYでbindする
	  --log       : ログを記録する
	  --elastic   : elasticsearchにログを記録する

## 設定ファイル
### orts.json
	listenするポートリストを記述する
		ports            : ポート設定のリスト
		name             : ログなどに出力される可読名称
		port             : listenするポート番号
		timeout          : 接続後に最初のパケットを受け取るまでのタイムアウト時間
		default_protocol : 上記タイムアウト時に接続しに行くプロトコル名(protocols.json内の定義名に対応)
		comment          : コメント

### protocols.json
	プロトコル判定方法と接続先のサーバーを記述する
		protocols        : プロトコル設定のリスト
		name             : ログなどに出力される可読名称(ports.json)
		server           : 接続先サーバー情報
		address          : サーバーのアドレス
		port             : サーバーのポート
		comment          : コメント
		rules            : プロトコル判定のルールリスト
		packet           : 最初の受信したパケット内容の判定を行う正規表現
		remote           : 対象のリモート情報の一致条件(現在、未実装)
		default_protocol : 全ての条件に一致しない場合ｎ使用するプロトコル名

### elastic.ini
	Elasticsearch接続先情報を記述する

## ログの形式
	ログは１件のログをJSON文字列化し１行の文字列として出力
		datetime         : ログ出力日時
		connection_id    : 1から順に振られるID
		type             : ログの種別
		  'accept'       : リモートから接続が行われた時のログ
		  'connect'      : プロトコルを決定しサーバへ接続したときのログ
		  'close'        : コネクションがクローズされた時のログ
		  'recv'         : リモートからサーバーへの受信データ
		  'send'         : サーバーからリモードへの送信データ
		client           : 接続時のクライアント側(インターネット)の情報
		server           : 接続時のサーバー側(ハニーポットなど)の情報
		remote           : antonaptから見てremoteにあたるソケットの情報(getpeernameの取得値)
		local            : antonapt自体のソケットの情報(getsocknameの取得値)
		address          : IPアドレス
		port             : ポート番号
		packetsize       : パケットのサイズ
		packet           : エスケープ処理を施したパケットの内容文字列(ASCII)
		                   長い場合packetsizeより短い長さに省略される場合がある

geopipは下記のURLからダウンロード
	https://dev.maxmind.com/geoip/geoip2/geolite2/

	下記に展開する
	detail/geoip/GeoLite2-ASN.mmdb
	detail/geoip/GeoLite2-City.mmdb
	detail/geoip/GeoLite2-Country.mmdb

<strong>This software is released under the MIT License, see LICENSE.txt.</strong>

