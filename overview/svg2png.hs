#!/usr/bin/env runghc

import System.Process
import System.Directory
import System.IO.Temp
import System.IO (hClose)
import Text.Pandoc.JSON

convertSvg :: FilePath -> FilePath -> IO ()
convertSvg src dest = callProcess "convert" [src, dest]

convertFilter :: Inline -> IO Inline
convertFilter (Image alt (url, title)) = do
    createDirectoryIfMissing False "images"
    (path, h) <- openTempFile "images" "image.svg"
    hClose h
    convertSvg url path
    return $ Image alt (path, title)
convertFilter other = return other

main :: IO ()
main = toJSONFilter convertFilter
