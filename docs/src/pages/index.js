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
    imageUrl: 'img/undraw_docusaurus_mountain.svg',
    description: (
      <>
        Define and apply your rules and policies.
        Integrate with your workflow.
      </>
    ),
  },
  {
    title: <>Extendable via plugins</>,
    imageUrl: 'img/undraw_docusaurus_mountain.svg',
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
    imageUrl: 'img/undraw_docusaurus_react.svg',
    description: (
      <>
        Complexity, size and other.
      </>
    ),
  },
  {
    title: <>Multiple languages</>,
    imageUrl: 'img/undraw_docusaurus_tree.svg',
    description: (
      <>
        C/C++, C# and Java.
        Recognises classes, interfaces, namespaces, functions, comments, preprocessor and much more.
      </>
    ),
  },
  {
    title: <>High performance and scalability</>,
    imageUrl: 'img/undraw_docusaurus_react.svg',
    description: (
      <>
        Applicable to huge code bases: thousands of files per minute.
        Ultra-fast feedback on iterative re-run.
        Effortless application to legacy code.
        Recognises legacy, modified and new code.
        Prevents from negative trends. Encourages positive.
      </>
    ),
  },
  {
    title: <>Effortless application to legacy code</>,
    imageUrl: 'img/undraw_docusaurus_react.svg',
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
        <div className="text--center">
          <img className={styles.featureImage} src={imgUrl} alt={title} />
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
      description="Description will go into a meta tag in <head />">
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
              to={useBaseUrl('docs/')}>
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
