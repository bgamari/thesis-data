import qualified Data.Sequence as S
import Data.Maybe (fromMaybe)
import Data.Foldable (toList)
import Data.List (scanl')
import Debug.Trace

-- Based on L.G. D'yachkov. "Analytical Solution of the Poisson-Boltzmann Equation
-- in Cases of Spherical and Axial Symmetry"

-- | Parameters for the Poisson-Boltzmann described by D'yachkov
data PoissonBoltzmann = PB { pbL       :: Double  -- ^ geometric parameter
                           , pbDelta   :: Double  -- ^ charge density imbalance factor
                           , pbA       :: Double  -- ^ radius of zero-potential boundary
                           }
-- | Produce the expansion parameters @b_n@.
coeffs :: PoissonBoltzmann    -- ^ radius of sphere
       -> [Double]  -- ^ successive approximations
coeffs (PB l delta a) = 1 : 0 : go' 0 (S.fromList [0,1])
  where
    -- Invariants:
    --   * `length bs` == n-1
    go' :: Int           -- ^ n
        -> S.Seq Double  -- ^ [b_{n+1}, b_n, b_{n-1}, ..., b_1, b_0]
        -> [Double]      -- ^ b_{n+2} : b_{n+3} : ...
    go' n bs =
        bp2 : go' (n+1) (bp2 S.<| bs)
      where
        bp2 =
            (2*l - 1) / (nn + 2) * getB (n+1)
          + 1 / (nn+1) / (nn+2) * (4*a^2 * ((1-delta) * getB n
                                            + delta * (3*bm1 - 3*bm2 + bm3))
                                   + s1)
        bm1 = getB (n-1)
        bm2 = getB (n-2)
        bm3 = getB (n-3)
        nn = realToFrac n :: Double

        s1 = sum $ map s1Term [0 .. n-1]
        s1Term :: Int -> Double
        s1Term k =
            (kk+1) * ( (kk+2) * getB (k+2) * (getB (n-k-1) - getB (n-k))
                     + (nn-kk+1) * getB (k+1) * (getB (n-k+1) - getB (n-k))
                     + 2*l * getB (k+1) * getB (n-k))
            + 4 * a^2 * getB k * (getB (n-k) + s2 k)
          where
            kk = realToFrac k :: Double

        s2 k = sum $ map (s2Term k) [0 .. n-k-1]
        s2Term k k' =
          getB k' * (getB (n-k-k')
                     - 3 * getB (n-k-k'-1)
                     + 3 * getB (n-k-k'-2)
                     - getB (n-k-k'-3))

        -- | @getB i@ is @b_i@
        getB :: Int -> Double
        getB i
          | i < 0            = 0
          | i >= S.length bs = error $ "index out of bounds "++show (i, bs, n)
          | otherwise        = S.index bs (1+n-i)

sphericalPB' :: PoissonBoltzmann  -- ^ parameters
             -> Double            -- ^ reparametrized distance @x@
             -> [Double]          -- ^ successive approximations of reparametrized potential @y@
sphericalPB' pb = \x -> scanl' (+) 0 $ zipWith (\i c -> c * x^i) [0..] cs
  where
    cs = coeffs pb

sphericalPB :: PoissonBoltzmann  -- ^ parameters
            -> Double            -- ^ distance @r@
            -> [Double]          -- ^ successive approximations of potential @phi@
sphericalPB pb = map yToPhi . sphericalPB' pb . rToX
  where
    yToPhi = log
    rToX r = 1 - sqrt (r / pbA pb)

b2, b3, b4 :: PoissonBoltzmann -> Double
b2 (PB l delta a) = 2 * a^2 * (1-delta)
b3 (PB l delta a) = 2/3 * a^2 * (1-delta) * (2*l - 3)
b4 (PB l delta a) = a^2/6 * (1-delta) * ((2*l-1)^2 + 2 + 8*a^2*(2-delta))

main :: IO ()
main = do
  let pb = PB {pbL=2, pbDelta=0.9, pbA=0.94}
  print $ (b2 pb, b3 pb, b4 pb)
  --print $ coeffs pb

  let f = withRelError 1e-4 . drop 3 . sphericalPB pb
  putStrLn $ unlines $ map (\r->show r++"\t"++show (f r)) (logSpace (-2) 0 500)

logSpace :: RealFloat a => a -> a -> Int -> [a]
logSpace a b n = [10**(a + d*realToFrac i) | i <- [0..n-1]]
  where
    d = (b-a) / realToFrac n

withRelError :: RealFrac a => a -> [a] -> a
withRelError tol = go
  where
    go (0:0:_) = 0
    go (x0:x1:rest)
      | abs ((x0-x1) / x1) < tol = x1
      | otherwise                = go (x1:rest)

