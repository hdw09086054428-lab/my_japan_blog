/**
 * 日本生活の老黄日記 - 多言語切り替えスクリプト（スローガン対応・最適化版）
 */
if (!localStorage.getItem('site-lang')) {
  localStorage.setItem('site-lang', 'ja');
}

function applyLanguage() {
    const lang = localStorage.getItem('site-lang') || 'ja';
    const isJa = (lang === 'ja');
    document.documentElement.lang = isJa ? 'ja' : 'zh-CN';
    // 1. クラスベースの表示切り替え（タイトル、本文、抜粋）
    document.querySelectorAll('.lang-ja').forEach(el => {
        el.style.setProperty('display', isJa ? '' : 'none', 'important');
    });
    document.querySelectorAll('.lang-zh').forEach(el => {
        el.style.setProperty('display', !isJa ? '' : 'none', 'important');
    });

    // 2. 「||」区切りテキストの自動分割
    // セレクタに #subtitle (スローガン) と .post-title-link (記事タイトルリンク) を追加
    const targets = '.navbar-brand, .nav-link, .banner-text .h1, .banner-text .h2, #subtitle, .post-title-link, .footer-content, .category-text, .tag-text';
    
    document.querySelectorAll(targets).forEach(el => {
        // data-raw属性を優先的にチェック
        let raw = el.getAttribute('data-raw') || el.innerText;
        
        if (raw && raw.includes('||')) {
            // 初回実行時に原文をdata-rawに保存
            if (!el.getAttribute('data-raw')) {
                el.setAttribute('data-raw', raw);
            }
            
            const parts = raw.split('||');
            if (parts.length >= 2) {
                const newText = isJa ? parts[0].trim() : parts[1].trim();
                
                // 無限ループ防止のため、テキストが異なる場合のみ更新
                if (el.innerText !== newText) {
                    el.innerText = newText;
                }
            }
        }
    });

    // 3. 記事内カバー画像の切り替え
    const coverEl = document.getElementById('dynamic-cover');
    if (coverEl) {
        coverEl.src = isJa ? "/img/cover_china_japan_fashion_jp.jpg" : "/img/cover_china_japan_fashion_cn.jpg";
    }
}

// 言語ボタンから呼ばれる関数
function switchLangBtn() {
    const current = localStorage.getItem('site-lang') || 'ja';
    const next = (current === 'ja' ? 'zh' : 'ja');
    localStorage.setItem('site-lang', next);
    applyLanguage();
}

// ページ読み込み完了時
document.addEventListener('DOMContentLoaded', applyLanguage);
window.addEventListener('load', applyLanguage);

// Fluidテーマの PJAX (ページ遷移) 対策
if (window.Fluid) {
    window.Fluid.utils.waitElementVisible('body', applyLanguage);
}

// MutationObserverによる動的な書き換えへの対応（無限ループ対策済み）
const observer = new MutationObserver((mutations) => {
    // 全体の変更を監視しつつ、言語切り替えが必要なタイミングで再実行
    // disconnectせずに最小限の負荷で実行するために、テキスト比較をapplyLanguage内で行っています
    applyLanguage();
});

// 監視を開始（スローガンのタイピングアニメーション終了などに対応）
observer.observe(document.body, { 
    childList: true, 
    subtree: true, 
    characterData: true 
});
