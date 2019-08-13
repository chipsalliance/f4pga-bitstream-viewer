module.exports = {
  publicPath: './',
  chainWebpack: (config) => {
    // disable prefetch as it chokes chromium
    config.plugins.delete('prefetch')
  },
};
