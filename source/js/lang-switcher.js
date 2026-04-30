/**
 * 日本生活の老黄日記 - 多言語切り替えスクリプト（著者対応・最適化版）
 */
if (!localStorage.getItem('site-lang')) {
  localStorage.setItem('site-lang', 'ja');
}

function applyLanguage() {
    const lang = localStorage.getItem('site-lang') || 'ja';
    const isJa = (lang === 'ja');
    document.documentElement.lang = isJa ? 'ja' : 'zh-CN';

    /* 1. クラスベースの表示切り替え（本文・タイトルなど） */
    document.querySelectorAll('.lang-ja').forEach(el => {
        el.style.setProperty('display', isJa ? '' : 'none', 'important');
    });
    document.querySelectorAll('.lang-zh').forEach(el => {
        el.style.setProperty('display', !isJa ? '' : 'none', 'important');
    });

    /* 2. 「||」区切りテキストの自動分割 */
    const targets = `
        .navbar-brand,
        .nav-link,
        .banner-text .h1,
        .banner-text .h2,
        #subtitle,
        .post-title-link,
        .footer-content,
        .category-text,
        .tag-text,
        .post-author-text
    `;

    document.querySelectorAll(targets).forEach(el => {
        let raw = el.getAttribute('data-raw') || el.innerText;

        if (raw && raw.includes('||')) {
            if (!el.getAttribute('data-raw')) {
                el.setAttribute('data-raw', raw);
            }

            const parts = raw.split('||');
            if (parts.length >= 2) {
                const newText = isJa ? parts[0].trim() : parts[1].trim();
                if (el.innerText !== newText) {
                    el.innerText = newText;
                }
            }
        }
    });

    /* 3. 記事内カバー画像の切り替え（必要に応じて） */
    const coverEl = document.getElementById('dynamic-cover');
    if (coverEl) {
        coverEl.src = isJa
            ? "/img/cover_china_japan_fashion_jp.jpg"
            : "/img/cover_china_japan_fashion_cn.jpg";
    }
}

/* 言語切り替えボタン */
function switchLangBtn() {
    const current = localStorage.getItem('site-lang') || 'ja';
    const next = (current === 'ja' ? 'zh' : 'ja');
    localStorage.setItem('site-lang', next);
    applyLanguage();
}

/* ページ読み込み */
document.addEventListener('DOMContentLoaded', applyLanguage);
window.addEventListener('load', applyLanguage);

/* Fluidテーマの PJAX 対策 */
if (window.Fluid) {
    window.Fluid.utils.waitElementVisible('body', applyLanguage);
}

/* MutationObserver（打字アニメーションなどの動的変更に対応） */
const observer = new MutationObserver(() => {
    applyLanguage();
});

observer.observe(document.body, {
    childList: true,
    subtree: true
});
