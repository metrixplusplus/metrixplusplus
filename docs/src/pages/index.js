import React from 'react';
import clsx from 'clsx';
import Layout from '@theme/Layout';
import Link from '@docusaurus/Link';
import useDocusaurusContext from '@docusaurus/useDocusaurusContext';
import useBaseUrl from '@docusaurus/useBaseUrl';
import styles from './styles.module.css';

const features = [
  {
    title: <>Configurable</>,
    imageUrl: 'img/perm_data_setting-24px.svg',
    description: (
      <>
        Define and apply your rules and policies.
        Integrate with your workflow.
      </>
    ),
  },
  {
    title: <>Extendable via plugins</>,
    imageUrl: 'img/extension-24px.svg',
    description: (
      <>
        Define your custom metric.
        Add new language parser.
        Create advanced post-analysis tool.
      </>
    ),
  },
  {
    title: <>Multiple metrics</>,
    imageUrl: 'img/analytics-24px.svg',
    description: (
      <>
        Complexity, size and other.
      </>
    ),
  },
  {
    title: <>Multiple languages</>,
    imageUrl: 'img/done_all-24px.svg',
    description: (
      <>
        C/C++, C# and Java.
        Recognizes classes, interfaces, namespaces, functions, comments, preprocessor and much more.
      </>
    ),
  },
  {
    title: <>High performance and scalability</>,
    imageUrl: 'img/speed-24px.svg',
    description: (
      <>
        Applicable to huge code bases: thousands of files per minute.
        Ultra-fast feedback on iterative re-run.
      </>
    ),
  },
  {
    title: <>Effortless application to legacy code</>,
    imageUrl: 'img/bolt-24px.svg',
    description: (
      <>
        Recognises legacy, modified and new code.
        Prevents from negative trends. Encourages positive.
      </>
    ),
  },
];

function Feature({imageUrl, title, description}) {
  const imgUrl = useBaseUrl(imageUrl);
  return (
    <div className={clsx('col col--4', styles.feature)}>
      {imgUrl && (
        <div className="text--center" style={{color:'green', fill: 'green'}}>
          <img className={styles.featureImage} style={{fill:'green'}} src={imgUrl} alt={title} />
        </div>
      )}
      <h3>{title}</h3>
      <p>{description}</p>
    </div>
  );
}

function Home() {
  const context = useDocusaurusContext();
  const {siteConfig = {}} = context;
  return (
    <Layout
      title={`${siteConfig.title}`}
      description="Management of source code quality is possible">
      <header className={clsx('hero hero--primary', styles.heroBanner)}>
        <div className="container">
          <h1 className="hero__title">{siteConfig.title}</h1>
          <p className="hero__subtitle">{siteConfig.tagline}</p>
          <div className={styles.buttons}>
            <Link
              className={clsx(
                'button button--outline button--secondary button--lg',
                styles.getStarted,
              )}
              to={useBaseUrl('docs/01-u-overview')}>
              Get Started
            </Link>
          </div>
        </div>
      </header>
      <main>
        {features && features.length > 0 && (
          <section className={styles.features}>
            <div className="container">
              <div className="row">
                {features.map((props, idx) => (
                  <Feature key={idx} {...props} />
                ))}
              </div>
            </div>
          </section>
        )}
      </main>
    </Layout>
  );
}

export default Home;
