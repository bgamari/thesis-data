import Control.Applicative
import Development.Shake
import Development.Shake.FilePath
import Data.List.Split (splitOn)

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

main :: IO ()
main = shakeArgs (shakeOptions {shakeThreads=0}) $ do
    "crunch-all" ~> do
        files <- concat <$> mapM (getFiles "timetag" . parseDate) dates
        liftIO $ print $ length files
        need $ map (`addExtension` "summary.svg") files

    "//*.timetag.summary.svg" %> \out -> do
        let timetag = dropExtension $ dropExtension out
        need [timetag]
        need ["scripts/summarize-fcs"]
        Exit c <- cmd "scripts/summarize-fcs" timetag
        return ()

    "output.pdf" %> \out -> do
        summaries <- concat <$> mapM (getFiles "timetag.summary.svg" . parseDate) dates
        cmd "svg-nup --no-tidy --nup 1x1 --no-landscape -o" out "--" summaries
