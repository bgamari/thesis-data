#!/usr/bin/env runghc

{-# LANGUAGE OverloadedStrings #-}

import Prelude hiding (takeWhile)
import Data.Maybe (fromMaybe)
import Control.Applicative
import Text.Printf
import Text.Pandoc.JSON
import Text.Pandoc.Walk
import Data.Attoparsec.Text
import qualified Data.Text as T

main = toJSONFilter filterDoc

data Summarize = Summarize { date :: String
                           , startRun, endRun :: Int
                           }

summarize :: Parser Summarize
summarize = do
    skipSpace
    "summarize:"
    skipSpace
    date <- takeWhile (/= ',')
    ","
    skipSpace
    start <- decimal
    end <- fmap (fromMaybe start) $ optional $ "-" *> decimal
    return $ Summarize (T.unpack date) start end

filterDoc :: Block -> Block
filterDoc (BlockQuote [body])
  | Right s <- parseOnly summarize $ T.pack $ blockToString body =
        let blocks = zipWith makeImg (map path runs) (map (\n->date s++", run "++showRunN n) runs)
            makeImg path caption = Para [Image [Str caption] (path, "fig:")]
            runs = [startRun s..endRun s]
            path n = "../by-date/all/"++date s++"/"++date s++"-run_"++showRunN n++".timetag.summary.svg"
            showRunN = printf "%03d"
        in Div nullAttr blocks
filterDoc blk = blk

blockToString :: Block -> String
blockToString = query inlineToString

inlineToString :: Inline -> String
inlineToString (Str s) = s
inlineToString Space = " "

