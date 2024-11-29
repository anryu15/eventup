function copyToClipboard() {
    // 現在のURLを取得
    const currentUrl = window.location.href;

    // コピー用のテキストエリアを作成してURLを設定
    const tempInput = document.createElement('textarea');
    tempInput.value = currentUrl;
    document.body.appendChild(tempInput);

    // テキストエリアを選択しコピー
    tempInput.select();
    document.execCommand('copy');

    // テキストエリアを削除
    document.body.removeChild(tempInput);

    // アラートを表示
    alert('Event URL copied to clipboard!');
}
