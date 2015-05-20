{-# LANGUAGE OverloadedStrings #-}
{-# LANGUAGE DeriveAnyClass #-}
{-# LANGUAGE DeriveGeneric #-}

import Control.Monad (guard, mzero)
import Control.Monad.Trans.Class
import Control.Monad.Trans.Maybe
import Control.Applicative
import Development.Shake
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

getFiles :: String -> Date String -> Action [FilePath]
getFiles ext (Date year month day) =
    getDirectoryFiles "." [concat ["by-date/",year,"/",year,"-",month,"/",year,"-",month,"-",day,"/*.",ext]]

lookupConfig :: FilePath -> MaybeT Action FileConfig
lookupConfig fname = do
    let configFile = takeDirectory fname </> "config.json"
    lift (doesFileExist configFile) >>= guard
    cfg <- MaybeT $ liftIO $ Aeson.decode <$> BS.readFile configFile
    MaybeT $ return $ HM.lookup (takeFileName fname) cfg

main :: IO ()
main = shakeArgs (shakeOptions {shakeThreads=0}) $ do
    getFileConfig <- addOracle $ runMaybeT . lookupConfig
    "crunch-all" ~> do
        files <- concat <$> mapM (getFiles "timetag" . parseDate) dates
        liftIO $ print $ length files
        need $ map (`addExtension` "summary.svg") files

    "//*.timetag.summary.svg" %> \out -> do
        let timetag = dropExtension $ dropExtension out
        getFileConfig timetag
        need [timetag]
        need ["scripts/summarize-fcs"]
        Exit c <- cmd ("scripts/summarize-fcs" :: String) timetag
        return ()

    "output.pdf" %> \out -> do
        summaries <- concat <$> mapM (getFiles "timetag.summary.svg" . parseDate) dates
        cmd ("svg-nup --no-tidy --nup 1x1 --no-landscape -o" :: String) out ("--" :: String) summaries
