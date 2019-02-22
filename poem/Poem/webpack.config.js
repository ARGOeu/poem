const webpack = require("webpack")
const path = require("path")
const BundleTracker = require("webpack-bundle-tracker")

module.exports = {
    entry: "./assets/js/index.js",
    output: {
        path: path.resolve("./assets/bundles/"),
        filename: "[name]-[hash].js",
        sourceMapFileName: "bundle.map"
    },
    devtool: "#source-map",
    module: {
        rules: [
            {
                test: /\.jsx?$/,
                exclude: /node_modules/,
                loader: 'babel-loader'
            }
        ]
    },
    plugins: [
        new BundleTracker({filename: './webpack-stats.json'}),
        new webpack.optimize.UglifyJsPlugin({
            sourceMap: true,
            warnings: false,
            mangle: true
        })
    ],
}
