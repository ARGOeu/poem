const webpack = require("webpack")
const path = require("path")
const BundleTracker = require("webpack-bundle-tracker")
const TerserPlugin = require("terser-webpack-plugin")
//const BundleAnalyzerPlugin = require('webpack-bundle-analyzer').BundleAnalyzerPlugin

module.exports = {
    entry: "./assets/js/index.js",
    node: {
        fs: 'empty',
        fsevents: 'empty',
        child_process: 'empty',
        module: 'empty'
    },
    output: {
        path: path.resolve("./assets/bundles/"),
        filename: "[name]-[hash].js",
        chunkFilename: "[name]-[hash].js"
    },
    mode: 'production',
    devtool: 'source-map',
    module: {
        rules: [
            {
                test: /\.jsx?$/,
                exclude: /node_modules/,
                loader: 'babel-loader',
                query: {
                    presets: ['@babel/env', '@babel/react']
                }
            }
        ]
    },
    plugins: [
        new BundleTracker({filename: './webpack-stats.json'}),
        //new BundleAnalyzerPlugin()
    ],
    optimization: {
        minimize: true,
        minimizer: [
        new TerserPlugin({
            cache: true,
            parallel: true,
            sourceMap: true,
        })
        ]
    }
}
