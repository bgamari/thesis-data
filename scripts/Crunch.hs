{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE DeriveAnyClass #-}
{-# LANGUAGE DeriveGeneric #-}
{-# LANGUAGE FlexibleContexts #-}

import System.Environment (getEnv)
import Control.Monad (guard, mzero)
import Control.Monad.Trans.Class
import Control.Monad.Trans.Maybe
import Control.Applicative
import Development.Shake hiding (getEnv)
import Development.Shake.FilePath
import Data.List.Split (splitOn)
import Data.Aeson as Aeson
import qualified Data.Vector as V
import qualified Data.ByteString.Lazy as BS
import qualified Data.HashMap.Strict as HM
import GHC.Generics
import Data.Binary
import Control.DeepSeq
import Data.Hashable

data Interval = Interval !Double !Double
              deriving (Show, Eq, Ord, Generic, Binary, NFData, Hashable)

instance FromJSON Interval where
    parseJSON (Array a) | V.length a == 2 = Interval <$> parseJSON (a V.! 0) <*> parseJSON (a V.! 1)
    parseJSON _ = mzero

data FileConfig = FileConfig { excludeTimes :: [Interval] }
                deriving (Show, Eq, Ord, Generic, Binary, NFData, Hashable)

instance FromJSON FileConfig where
    parseJSON (Object o) = FileConfig <$> o .:? "exclude" .!= []
    parseJSON _ = mzero

dates :: [String]
dates = words "2015-05-05 2015-05-02 2015-04-22 2015-04-20 2015-04-19 2015-04-15 2015-03-19 2015-03-12 2015-02-19 2015-02-12"

data Date a = Date {year, month, day :: a}

parseDate :: String -> Date String
parseDate s =
    let year:month:day:_ = splitOn "-" s
    in Date year month day

dateDir :: Date String -> FilePath
dateDir (Date year month day) =
    "by-date" </> year </> (year<->month) </> (year<->month<->day)
  where a <-> b = a ++ "-" ++ b

getFiles :: String -> Date String -> Action [FilePath]
getFiles ext date =
    getDirectoryFiles "." [dateDir date </> "*." ++ ext]

lookupConfig :: FilePath -> MaybeT Action FileConfig
lookupConfig fname = do
    let configFile = takeDirectory fname </> "config.json"
    lift (doesFileExist configFile) >>= guard
    cfg <- MaybeT $ liftIO $ Aeson.decode <$> BS.readFile configFile
    MaybeT $ return $ HM.lookup (takeFileName fname) cfg


getTimetags :: Action [FilePath]
getTimetags = concat <$> mapM (getFiles "timetag" . parseDate) dates

main :: IO ()
main = do
    dataRoot <- getEnv "data_root"
    let shakeOpts = shakeOptions
                    { shakeThreads = 0
                    , shakeStaunch = True
                    , shakeProgress = progressSimple
                    , shakeFiles = dataRoot </> ".shake"
                    }
    shakeArgs shakeOpts (rules dataRoot)

rules :: FilePath -> Rules ()
rules dataRoot = do
    getFileConfig <- addOracle $ runMaybeT . lookupConfig
    phony "crunch-all" $ do
        files <- getTimetags
        liftIO $ print $ length files
        need $ map (`addExtension` "summary.svg") files

    "//*.timetag.summary.svg" %> \out -> do
        let timetag = dropExtension $ dropExtension out
            summarize = dataRoot</>"scripts/summarize-fcs"
        getFileConfig timetag
        need [timetag, summarize, timetag <.> "xcorr-0-1"]
        Exit c <- command [] summarize [timetag]
        return ()

    "output.pdf" %> \out -> do
        summaries <- concat <$> mapM (getFiles "timetag.summary.svg" . parseDate) dates
        command [] "svg-nup" (words "--no-tidy --nup 1x1 --no-landscape -o"++[out, "--"]++summaries)

    "//*.timetag.xcorr-0-1" %> \out -> do
        let timetag = dropExtension out
        need [timetag]
        cfg <- getFileConfig timetag
        let excludeInterval (Interval s e) = "-e"++show s++"-"++show e
            args = [timetag, "--engine=hphoton", "-n0", "-E100e-9", "-L10", "--plot", "--output="++takeDirectory timetag]
                   ++ map excludeInterval (maybe [] excludeTimes cfg)
        command [] "fcs-corr" args

    phony "corr-all" $ do
        getTimetags >>= need . map (<.> "xcorr-0-1")

    "//corr" %> \out -> do
        let dir = takeDirectory out
        timetags <- getDirectoryFiles "." ["*.timetag"]
        need $ map (<.> "xcorr-0-1") timetags
