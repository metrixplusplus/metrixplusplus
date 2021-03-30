module.exports = {
  title: 'Metrix++',
  tagline: 'Management of source code quality is possible',
  url: 'https://metrixplusplus.github.io/',
  baseUrl: '/metrixplusplus/',
  favicon: 'img/favicon.png',
  projectName: 'metrixplusplus', // Usually your repo name.
  themeConfig: {
    navbar: {
      title: 'Metrix++',
      logo: {
        alt: 'Metrix++',
        src: 'img/favicon.png',
      },
      items: [
        {
          to: 'docs/01-u-overview',
          activeBasePath: 'docs',
          label: 'Docs',
          position: 'left',
        },
        {
          href: 'https://github.com/metrixplusplus/metrixplusplus',
          label: 'GitHub',
          position: 'right',
        },
      ],
    },
    footer: {
      style: 'dark',
      links: [
        {
          title: 'Docs',
          items: [
            {
              label: 'Users Manual',
              to: 'docs/01-u-overview',
            },
            {
              label: 'Developers Manual',
              to: 'docs/01-d-file',
            },
          ],
        },
        {
          title: 'Community',
          items: [
            {
              label: 'GitHub',
              href: 'https://github.com/metrixplusplus/',
            },
            {
              label: 'Open issues',
              href: 'https://github.com/metrixplusplus/metrixplusplus/issues',
            },
            {
              label: 'Changelog',
              href: 'https://github.com/metrixplusplus/metrixplusplus/blob/master/CHANGELOG.md',
            },
          ],
        },
        {
          title: 'Feedback',
          items: [
            {
              label: 'Ask question',
              href: 'https://github.com/metrixplusplus/metrixplusplus/issues/new',
            },
            {
              label: 'Report defect',
              href: 'https://github.com/metrixplusplus/metrixplusplus/issues/new',
            },
            {
              label: 'Feature request',
              href: 'https://github.com/metrixplusplus/metrixplusplus/issues/new',
            },
          ],
        },
      ],
      copyright: `Copyright © 2009 - ${new Date().getFullYear()}, Metrix++ Project.`,
    },
  },
  presets: [
    [
      '@docusaurus/preset-classic',
      {
        docs: {
          // It is recommended to set document id as docs home page (`docs/` path).
          homePageId: 'highlights',
          sidebarPath: require.resolve('./sidebars.js'),
          // Please change this to your repo.
          editUrl:
            'https://metrixplusplus.github.io/',
        },
        blog: {
          showReadingTime: true,
          // Please change this to your repo.
          editUrl:
            'https://metrixplusplus.github.io/',
        },
        theme: {
          customCss: require.resolve('./src/css/custom.css'),
        },
      },
    ],
  ],
};
