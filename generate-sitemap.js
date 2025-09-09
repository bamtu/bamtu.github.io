const SitemapGenerator = require('sitemap-generator');

// 사이트의 URL을 입력합니다.
const generator = SitemapGenerator('https://bamtu.github.io', {
  stripQuerystring: false, // 쿼리 문자열을 제거하지 않도록 설정
  filepath: './sitemap.xml', // 생성된 사이트맵 파일의 경로
  maxEntriesPerFile: 50000, // 한 파일당 최대 50,000개의 URL을 설정
});

// 생성 완료 후 실행할 작업을 정의합니다.
generator.on('done', () => {
  console.log('사이트맵 생성 완료!');
});

// 크롤링 시작
generator.start();
